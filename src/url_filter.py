"""
URL Filter module for intelligent content inclusion filtering.

This module implements LLM-based filtering to evaluate crawled content
and make binary include/exclude decisions for the target documentation goal.
"""

import asyncio
from typing import List, Dict, Any, Optional, Tuple
import json
from openai import AsyncOpenAI

from .config import LLMConfig, FilterLLMConfig


class URLFilter:
    """
    LLM-based filter that evaluates crawled content and makes binary
    include/exclude decisions for a specific documentation target before expensive parsing.
    """
    
    def __init__(self, filter_llm_config: Optional[FilterLLMConfig] = None, target_topic: str = ""):
        """
        Initialize the URL filter with dedicated filtering model configuration.
        
        Args:
            filter_llm_config: Configuration for the filtering LLM (separate from extraction LLM)
            target_topic: The specific topic/goal for filtering (e.g., "Python SDK documentation")
        """
        self.filter_llm_config = filter_llm_config or FilterLLMConfig()
        self.filter_llm_config.validate()  # Ensure required config is present
        self.target_topic = target_topic
        self.client = AsyncOpenAI(api_key=self.filter_llm_config.api_key)
    
    async def filter_crawled_results(self, crawled_results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Filter crawled results based on binary include/exclude decisions for target topic.
        
        Args:
            crawled_results: List of crawled page results
            
        Returns:
            Filtered list of included crawled results
        """
        if not crawled_results:
            return []
        
        print(f"Filtering {len(crawled_results)} crawled pages for inclusion based on: {self.target_topic}")
        
        # Analyze each page for inclusion
        filtered_results = []
        for i, result in enumerate(crawled_results):
            print(f"Analyzing page {i+1}/{len(crawled_results)}: {result['url']}")
            
            try:
                should_include, explanation = await self._analyze_page_inclusion(result)
                
                if should_include:
                    # Add decision metadata to the result
                    result['included'] = True
                    result['decision_explanation'] = explanation
                    filtered_results.append(result)
                    print(f"✅ Included: {result['url']}")
                else:
                    print(f"❌ Excluded: {result['url']}")
                    
            except Exception as e:
                print(f"⚠️  Error analyzing {result['url']}: {e}")
                # Include pages that couldn't be analyzed to be safe
                result['included'] = True
                result['decision_explanation'] = f"Analysis failed: {e}"
                filtered_results.append(result)
        
        print(f"Filtered results: {len(filtered_results)}/{len(crawled_results)} pages kept")
        return filtered_results
    
    async def _analyze_page_inclusion(self, page_result: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Analyze a single page for inclusion using LLM binary decision.
        
        Args:
            page_result: Single crawled page result
            
        Returns:
            Tuple of (should_include, explanation)
        """
        # Prepare content for analysis
        url = page_result.get('url', '')
        title = page_result.get('title', '')
        
        # Get a sample of the content (first 2000 chars to stay within token limits)
        content_sample = ""
        if 'cleaned_html' in page_result:
            content_sample = page_result['cleaned_html'][:2000]
        elif 'html' in page_result:
            content_sample = page_result['html'][:2000]
        
        # Create the analysis prompt
        prompt = self._create_inclusion_prompt(url, title, content_sample)
        
        try:
            # Check if this is an o1 model (which doesn't support system messages)
            model_name = self.filter_llm_config.provider.split('/')[-1]
            is_o1_model = 'o1' in model_name.lower()
            
            if is_o1_model:
                # o1 models don't support system messages, so combine into user message
                combined_prompt = f"""You are an expert at analyzing web content for documentation inclusion decisions.

{prompt}"""
                messages = [{"role": "user", "content": combined_prompt}]
                # o1 models also don't support temperature or max_tokens parameters
                response = await self.client.chat.completions.create(
                    model=model_name,
                    messages=messages
                )
            else:
                # Standard models support system messages and parameters
                messages = [
                    {"role": "system", "content": "You are an expert at analyzing web content for documentation inclusion decisions."},
                    {"role": "user", "content": prompt}
                ]
                response = await self.client.chat.completions.create(
                    model=model_name,
                    messages=messages,
                    temperature=self.filter_llm_config.temperature,
                    max_tokens=500
                )
            
            # Parse the response
            response_text = response.choices[0].message.content.strip()
            return self._parse_inclusion_response(response_text)
            
        except Exception as e:
            print(f"LLM analysis failed: {e}")
            return True, f"Analysis failed: {e}"
    
    def _create_inclusion_prompt(self, url: str, title: str, content_sample: str) -> str:
        """
        Create the prompt for binary inclusion analysis.
        
        Args:
            url: Page URL
            title: Page title
            content_sample: Sample of page content
            
        Returns:
            Formatted prompt for LLM analysis
        """
        return f"""
Analyze this web page and decide whether to INCLUDE or EXCLUDE it for the target topic: "{self.target_topic}"

Page Details:
- URL: {url}
- Title: {title}
- Content Sample: {content_sample}

Make a binary decision based on relevance to the target topic.

Respond in this exact JSON format:
{{
    "decision": "include",
    "explanation": "Brief explanation of why this page should be included or excluded"
}}

The "decision" field must be exactly "include" or "exclude".

Consider factors like:
- Does the content directly address the target topic?
- Are there specific technical details related to the target?
- Is this a navigation page vs. actual documentation content?
- Does the URL path indicate relevance?
- Does the title suggest relevant content?
"""
    
    def _parse_inclusion_response(self, response_text: str) -> Tuple[bool, str]:
        """
        Parse the LLM response to extract binary decision and explanation.
        
        Args:
            response_text: Raw response from LLM
            
        Returns:
            Tuple of (should_include, explanation)
        """
        try:
            # Try to parse as JSON
            if '{' in response_text and '}' in response_text:
                # Extract JSON part
                start = response_text.find('{')
                end = response_text.rfind('}') + 1
                json_str = response_text[start:end]
                
                data = json.loads(json_str)
                decision = data.get('decision', '').lower().strip()
                explanation = data.get('explanation', 'No explanation provided')
                
                # Convert decision to boolean
                should_include = decision == 'include'
                
                return should_include, explanation
            else:
                # Fallback: look for include/exclude keywords in text
                response_lower = response_text.lower()
                if 'include' in response_lower and 'exclude' not in response_lower:
                    return True, response_text
                elif 'exclude' in response_lower and 'include' not in response_lower:
                    return False, response_text
                else:
                    # Default to include if unclear
                    return True, f"Could not parse clear decision: {response_text}"
                    
        except Exception as e:
            return True, f"Parse error: {e}"
    
    def set_target_topic(self, target_topic: str):
        """
        Set or update the target topic for filtering.
        
        Args:
            target_topic: New target topic description
        """
        self.target_topic = target_topic
        print(f"Updated target topic to: {target_topic}")