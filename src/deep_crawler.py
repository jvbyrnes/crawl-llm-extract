"""
Deep Crawler module for API documentation crawling.

This module implements the deep crawling functionality using strategies from crawl4ai.
"""

import asyncio
from typing import List, Dict, Any, Optional

from crawl4ai import AsyncWebCrawler, CrawlerRunConfig
from crawl4ai.deep_crawling import BestFirstCrawlingStrategy
from crawl4ai.deep_crawling.scorers import KeywordRelevanceScorer
from crawl4ai.content_scraping_strategy import LXMLWebScrapingStrategy

from .config import CrawlerConfig


class DeepCrawler:
    """
    Implements deep crawling functionality using strategies from crawl4ai.
    Simplified to focus on core functionality.
    """
    
    def __init__(self, config: Optional[CrawlerConfig] = None):
        """
        Initialize with optional configuration.
        
        Args:
            config: Configuration for the crawler (CrawlerConfig)
        """
        self.config = config or CrawlerConfig()
        self.crawler = None
        
    async def crawl(self, url: str) -> List[Dict[str, Any]]:
        """
        Crawl the specified URL using the configured strategy.
        
        Args:
            url: URL to crawl
            
        Returns:
            Crawled results
        """
        # Validate configuration
        self.config.validate()
        
        # Create a scorer if keywords are provided
        scorer = None
        if self.config.keywords:
            scorer = KeywordRelevanceScorer(
                keywords=self.config.keywords,
                weight=self.config.weight
            )
        
        # Configure the strategy
        strategy = BestFirstCrawlingStrategy(
            max_depth=self.config.max_depth,
            include_external=self.config.include_external,
            url_scorer=scorer,
            max_pages=self.config.max_pages
        )
        
        # Configure the crawler
        run_config = CrawlerRunConfig(
            deep_crawl_strategy=strategy,
            scraping_strategy=LXMLWebScrapingStrategy(),
            verbose=True
        )
        
        # Initialize and run the crawler
        async with AsyncWebCrawler() as crawler:
            self.crawler = crawler
            try:
                results = await crawler.arun(url, config=run_config)
                return [self._process_result(result) for result in results]
            except Exception as e:
                # Basic error handling
                print(f"Error during crawling: {e}")
                return []
    
    def _process_result(self, result: Any) -> Dict[str, Any]:
        """
        Process a crawler result into a standardized format.
        
        Args:
            result: Result from the crawler
            
        Returns:
            Processed result
        """
        return {
            'url': result.url,
            'html': result.html,
            'cleaned_html': result.cleaned_html if hasattr(result, 'cleaned_html') else result.html,
            'depth': result.metadata.get('depth', 0) if hasattr(result, 'metadata') else 0,
            'title': result.metadata.get('title', '') if hasattr(result, 'metadata') else '',
        }