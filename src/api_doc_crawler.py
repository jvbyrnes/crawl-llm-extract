"""
API Documentation Crawler module.

This module implements the high-level orchestrator that coordinates the crawling and parsing process.
"""

import os
import asyncio
from typing import List, Dict, Any, Optional
import json

from .config import CrawlerConfig, LLMConfig, FilterLLMConfig
from .deep_crawler import DeepCrawler
from .llm_parser import LLMParser
from .url_filter import URLFilter


class ApiDocCrawler:
    """
    High-level orchestrator that coordinates the crawling and parsing process.
    Simplified to focus on core functionality.
    """
    
    def __init__(self, crawler_config: Optional[CrawlerConfig] = None,
                 llm_config: Optional[LLMConfig] = None,
                 filter_llm_config: Optional[FilterLLMConfig] = None,
                 target_topic: str = ""):
        """
        Initialize with optional configurations for dual-model architecture.
        
        Args:
            crawler_config: Configuration for the crawler (CrawlerConfig)
            llm_config: Configuration for the extraction LLM (LLMConfig)
            filter_llm_config: Configuration for the filtering LLM (FilterLLMConfig)
            target_topic: Target topic for URL filtering (e.g., "Python SDK documentation")
        """
        self.crawler_config = crawler_config or CrawlerConfig()
        self.llm_config = llm_config or LLMConfig()
        self.filter_llm_config = filter_llm_config or FilterLLMConfig()
        self.target_topic = target_topic
        self.deep_crawler = DeepCrawler(self.crawler_config)
        self.llm_parser = LLMParser(self.llm_config)
        self.url_filter = URLFilter(self.filter_llm_config, target_topic)
    
    async def crawl_and_parse(self, url: str, relevance_threshold: float = 0.7) -> List[Dict[str, Any]]:
        """
        Crawl the API documentation, filter for relevance, and parse the content.
        
        Args:
            url: URL of the API documentation
            relevance_threshold: Minimum relevance score (0.0-1.0) to include page
            
        Returns:
            Processed results
        """
        # Crawl the URL
        print(f"Crawling {url}...")
        crawler_results = await self.deep_crawler.crawl(url)
        
        if not crawler_results:
            print("No results found during crawling.")
            return []
        
        print(f"Found {len(crawler_results)} pages.")
        
        # Filter results for relevance if target topic is specified
        if self.target_topic:
            print(f"Filtering for relevance to: {self.target_topic}")
            crawler_results = await self.url_filter.filter_crawled_results(
                crawler_results, relevance_threshold
            )
            
            if not crawler_results:
                print("No relevant pages found after filtering.")
                return []
            
            print(f"After filtering: {len(crawler_results)} relevant pages.")
        else:
            print("No target topic specified, skipping relevance filtering.")
        
        # Parse each filtered result
        parsed_results = []
        for i, result in enumerate(crawler_results):
            print(f"Parsing page {i+1}/{len(crawler_results)}: {result['url']}")
            
            try:
                parsed_content = await self.llm_parser.parse(result['cleaned_html'])
                
                parsed_result = {
                    'url': result['url'],
                    'title': result['title'],
                    'depth': result['depth'],
                    'content': parsed_content
                }
                
                # Include relevance metadata if available
                if 'relevance_score' in result:
                    parsed_result['relevance_score'] = result['relevance_score']
                    parsed_result['relevance_explanation'] = result['relevance_explanation']
                
                parsed_results.append(parsed_result)
                
                print(f"Successfully parsed {result['url']}")
            except Exception as e:
                print(f"Error parsing {result['url']}: {e}")
        
        return parsed_results
    
    async def crawl_only(self, url: str, relevance_threshold: float = 0.7) -> List[Dict[str, Any]]:
        """
        Only crawl the API documentation without parsing, with optional filtering.
        
        Args:
            url: URL of the API documentation
            relevance_threshold: Minimum relevance score (0.0-1.0) to include page
            
        Returns:
            Crawled results (filtered if target topic is specified)
        """
        crawler_results = await self.deep_crawler.crawl(url)
        
        # Filter results for relevance if target topic is specified
        if self.target_topic and crawler_results:
            print(f"Filtering crawled results for relevance to: {self.target_topic}")
            crawler_results = await self.url_filter.filter_crawled_results(
                crawler_results, relevance_threshold
            )
        
        return crawler_results
    
    async def parse_only(self, html_content: str) -> List[str]:
        """
        Only parse the provided HTML content without crawling.
        
        Args:
            html_content: HTML content to parse
            
        Returns:
            Parsed results
        """
        return await self.llm_parser.parse(html_content)
    
    def set_target_topic(self, target_topic: str):
        """
        Set or update the target topic for URL filtering.
        
        Args:
            target_topic: Target topic description (e.g., "Python SDK documentation")
        """
        self.target_topic = target_topic
        self.url_filter.set_target_topic(target_topic)
        print(f"Updated target topic to: {target_topic}")
    
    def set_filter_llm_config(self, filter_llm_config: FilterLLMConfig):
        """
        Set or update the filter LLM configuration.
        
        Args:
            filter_llm_config: New filter LLM configuration
        """
        self.filter_llm_config = filter_llm_config
        self.url_filter = URLFilter(filter_llm_config, self.target_topic)
        print(f"Updated filter LLM config to: {filter_llm_config}")
    
    def save_results(self, results: List[Dict[str, Any]], output_dir: str = "output") -> None:
        """
        Save the results to files.
        
        Args:
            results: Results to save
            output_dir: Directory to save the results in
        """
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        # Save each result
        for i, result in enumerate(results):
            # Create a safe filename from the URL
            filename_base = f"page_{i+1}"
            
            # Save the content as markdown
            if result.get('content'):
                md_path = os.path.join(output_dir, f"{filename_base}.md")
                with open(md_path, 'w', encoding='utf-8') as f:
                    f.write("\n".join(result['content']))
            
            # Save the metadata as JSON (including relevance info if available)
            meta = {k: v for k, v in result.items() if k != 'content'}
            json_path = os.path.join(output_dir, f"{filename_base}_meta.json")
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(meta, f, indent=2)
        
        # Save the index file
        index_path = os.path.join(output_dir, "index.json")
        with open(index_path, 'w', encoding='utf-8') as f:
            index = []
            for i, r in enumerate(results):
                if r.get('content'):
                    entry = {
                        'url': r['url'],
                        'title': r.get('title', ''),
                        'depth': r.get('depth', 0),
                        'filename': f"page_{i+1}.md"
                    }
                    # Include relevance info if available
                    if 'relevance_score' in r:
                        entry['relevance_score'] = r['relevance_score']
                        entry['relevance_explanation'] = r.get('relevance_explanation', '')
                    index.append(entry)
            json.dump(index, f, indent=2)
        
        print(f"Results saved to {output_dir}")