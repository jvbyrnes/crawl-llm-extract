"""
API Documentation Crawler module.

This module implements the high-level orchestrator that coordinates the crawling and parsing process.
"""

import os
import asyncio
from typing import List, Dict, Any, Optional
import json

from .config import CrawlerConfig, LLMConfig
from .deep_crawler import DeepCrawler
from .llm_parser import LLMParser


class ApiDocCrawler:
    """
    High-level orchestrator that coordinates the crawling and parsing process.
    Simplified to focus on core functionality.
    """
    
    def __init__(self, crawler_config: Optional[CrawlerConfig] = None, llm_config: Optional[LLMConfig] = None):
        """
        Initialize with optional configurations.
        
        Args:
            crawler_config: Configuration for the crawler (CrawlerConfig)
            llm_config: Configuration for the LLM (LLMConfig)
        """
        self.crawler_config = crawler_config or CrawlerConfig()
        self.llm_config = llm_config or LLMConfig()
        self.deep_crawler = DeepCrawler(self.crawler_config)
        self.llm_parser = LLMParser(self.llm_config)
    
    async def crawl_and_parse(self, url: str) -> List[Dict[str, Any]]:
        """
        Crawl the API documentation and parse the content.
        
        Args:
            url: URL of the API documentation
            
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
        
        # Parse each result
        parsed_results = []
        for i, result in enumerate(crawler_results):
            print(f"Parsing page {i+1}/{len(crawler_results)}: {result['url']}")
            
            try:
                parsed_content = await self.llm_parser.parse(result['cleaned_html'])
                
                parsed_results.append({
                    'url': result['url'],
                    'title': result['title'],
                    'depth': result['depth'],
                    'content': parsed_content
                })
                
                print(f"Successfully parsed {result['url']}")
            except Exception as e:
                print(f"Error parsing {result['url']}: {e}")
        
        return parsed_results
    
    async def crawl_only(self, url: str) -> List[Dict[str, Any]]:
        """
        Only crawl the API documentation without parsing.
        
        Args:
            url: URL of the API documentation
            
        Returns:
            Crawled results
        """
        return await self.deep_crawler.crawl(url)
    
    async def parse_only(self, html_content: str) -> List[str]:
        """
        Only parse the provided HTML content without crawling.
        
        Args:
            html_content: HTML content to parse
            
        Returns:
            Parsed results
        """
        return await self.llm_parser.parse(html_content)
    
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
            
            # Save the metadata as JSON
            meta = {k: v for k, v in result.items() if k != 'content'}
            json_path = os.path.join(output_dir, f"{filename_base}_meta.json")
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(meta, f, indent=2)
        
        # Save the index file
        index_path = os.path.join(output_dir, "index.json")
        with open(index_path, 'w', encoding='utf-8') as f:
            index = [{
                'url': r['url'],
                'title': r.get('title', ''),
                'depth': r.get('depth', 0),
                'filename': f"page_{i+1}.md"
            } for i, r in enumerate(results) if r.get('content')]
            json.dump(index, f, indent=2)
        
        print(f"Results saved to {output_dir}")