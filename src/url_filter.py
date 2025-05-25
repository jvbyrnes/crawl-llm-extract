"""
URL Filter module for intelligent content relevance filtering.

This module implements LLM-based filtering to evaluate crawled content
and determine which pages are most relevant to the target documentation goal.
"""

import asyncio
from typing import List, Dict, Any, Optional, Tuple
import json
from openai import AsyncOpenAI

from .config import LLMConfig, FilterLLMConfig


class URLFilter:
    """
    LLM-based filter that evaluates crawled content for relevance
    to a specific documentation target before expensive parsing.
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
    
    async def filter_crawled_results(self, crawled_results: List[Dict[str, Any]], 
                                   relevance_threshold: float = 0.7) -> List[Dict[str, Any]]:
        """
        Filter crawled results based on relevance to target topic.
        
        Args:
            crawled_results: List of crawled page results
            relevance_threshold: Minimum relevance score (0.0-1.0) to include page
            
        Returns:
            Filtered list of relevant crawled results
        """
        if not crawled_results:
            return []
        
        print(f"Filtering {len(crawled_results)} crawled pages for relevance to: {self.target_topic}")
        
        # Analyze each page for relevance
        filtered_results = []
        for i, result in enumerate(crawled_results):
            print(f"Analyzing page {i+1}/{len(crawled_results)}: {result['url']}")
            
            try:
                relevance_score, explanation = await self._analyze_page_relevance(result)
                
                if relevance_score >= relevance_threshold:
                    # Add relevance metadata to the result
                    result['relevance_score'] = relevance_score
                    result['relevance_explanation'] = explanation
                    filtered_results.append(result)
                    print(f"✅ Included (score: {relevance_score:.2f}): {result['url']}")
                else:
                    print(f"❌ Filtered out (score: {relevance_score:.2f}): {result['url']}")
                    
            except Exception as e:
                print(f"⚠️  Error analyzing {result['url']}: {e}")
                # Include pages that couldn't be analyzed to be safe
                result['relevance_score'] = 0.5
                result['relevance_explanation'] = f"Analysis failed: {e}"
                filtered_results.append(result)
        
        print(f"Filtered results: {len(filtered_results)}/{len(crawled_results)} pages kept")
        return filtered_results
    
    async def _analyze_page_relevance(self, page_result: Dict[str, Any]) -> Tuple[float, str]:
        """
        Analyze a single page for relevance using LLM.
        
        Args:
            page_result: Single crawled page result
            
        Returns:
            Tuple of (relevance_score, explanation)
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
        prompt = self._create_relevance_prompt(url, title, content_sample)
        
        try:
            # Check if this is an o1 model (which doesn't support system messages)
            model_name = self.filter_llm_config.provider.split('/')[-1]
            is_o1_model = 'o1' in model_name.lower()
            
            if is_o1_model:
                # o1 models don't support system messages, so combine into user message
                combined_prompt = f"""You are an expert at analyzing web content for documentation relevance.

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
                    {"role": "system", "content": "You are an expert at analyzing web content for documentation relevance."},
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
            return self._parse_relevance_response(response_text)
            
        except Exception as e:
            print(f"LLM analysis failed: {e}")
            return 0.5, f"Analysis failed: {e}"
    
    def _create_relevance_prompt(self, url: str, title: str, content_sample: str) -> str:
        """
        Create the prompt for relevance analysis.
        
        Args:
            url: Page URL
            title: Page title
            content_sample: Sample of page content
            
        Returns:
            Formatted prompt for LLM analysis
        """
        return f"""
Analyze this web page for relevance to the target topic: "{self.target_topic}"

Page Details:
- URL: {url}
- Title: {title}
- Content Sample: {content_sample}

Please evaluate how relevant this page is to the target topic on a scale of 0.0 to 1.0:
- 1.0 = Highly relevant, directly related to the target topic
- 0.7-0.9 = Moderately relevant, contains useful related information
- 0.4-0.6 = Somewhat relevant, tangentially related
- 0.1-0.3 = Minimally relevant, barely related
- 0.0 = Not relevant, unrelated to the target topic

Respond in this exact JSON format:
{{
    "relevance_score": 0.8,
    "explanation": "Brief explanation of why this page is or isn't relevant to the target topic"
}}

Consider factors like:
- Does the content directly address the target topic?
- Are there specific technical details related to the target?
- Is this a navigation page vs. actual documentation content?
- Does the URL path indicate relevance?
- Does the title suggest relevant content?
"""
    
    def _parse_relevance_response(self, response_text: str) -> Tuple[float, str]:
        """
        Parse the LLM response to extract relevance score and explanation.
        
        Args:
            response_text: Raw response from LLM
            
        Returns:
            Tuple of (relevance_score, explanation)
        """
        try:
            # Try to parse as JSON
            if '{' in response_text and '}' in response_text:
                # Extract JSON part
                start = response_text.find('{')
                end = response_text.rfind('}') + 1
                json_str = response_text[start:end]
                
                data = json.loads(json_str)
                score = float(data.get('relevance_score', 0.5))
                explanation = data.get('explanation', 'No explanation provided')
                
                # Ensure score is within valid range
                score = max(0.0, min(1.0, score))
                
                return score, explanation
            else:
                # Fallback: try to extract score from text
                import re
                score_match = re.search(r'(\d+\.?\d*)', response_text)
                if score_match:
                    score = float(score_match.group(1))
                    if score > 1.0:  # Handle cases where score might be out of 10
                        score = score / 10.0
                    score = max(0.0, min(1.0, score))
                    return score, response_text
                else:
                    return 0.5, f"Could not parse response: {response_text}"
                    
        except Exception as e:
            return 0.5, f"Parse error: {e}"
    
    def set_target_topic(self, target_topic: str):
        """
        Set or update the target topic for filtering.
        
        Args:
            target_topic: New target topic description
        """
        self.target_topic = target_topic
        print(f"Updated target topic to: {target_topic}")