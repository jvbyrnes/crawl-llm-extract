"""
Main script for the API documentation crawler.

This script demonstrates how to use the API documentation crawler.
"""

import asyncio
import argparse
from typing import Optional

from .config import CrawlerConfig, LLMConfig
from .api_doc_crawler import ApiDocCrawler


async def main(url: str, output_dir: str = "output", keywords: Optional[str] = None,
               max_depth: int = 2, max_pages: int = 25, include_external: bool = False) -> None:
    """
    Main function for the API documentation crawler.
    
    Args:
        url: URL of the API documentation
        output_dir: Directory to save the results in
        keywords: Comma-separated list of keywords for relevance scoring
        max_depth: Maximum depth for crawling
        max_pages: Maximum number of pages to crawl
        include_external: Whether to include external links
    """
    # Create configurations
    crawler_config = CrawlerConfig(
        max_depth=max_depth,
        include_external=include_external,
        max_pages=max_pages
    )
    
    if keywords:
        crawler_config.set_keywords(keywords.split(','))
    
    llm_config = LLMConfig()
    
    # Create the crawler
    crawler = ApiDocCrawler(crawler_config, llm_config)
    
    # Crawl and parse
    results = await crawler.crawl_and_parse(url)
    
    # Save results
    crawler.save_results(results, output_dir)
    
    print(f"Processed {len(results)} pages from {url}")


if __name__ == "__main__":
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="API Documentation Crawler")
    parser.add_argument("url", help="URL of the API documentation")
    parser.add_argument("--output-dir", default="output", help="Directory to save the results in")
    parser.add_argument("--keywords", help="Comma-separated list of keywords for relevance scoring")
    parser.add_argument("--max-depth", type=int, default=2, help="Maximum depth for crawling")
    parser.add_argument("--max-pages", type=int, default=25, help="Maximum number of pages to crawl")
    parser.add_argument("--include-external", action="store_true", help="Include external links")
    
    args = parser.parse_args()
    
    # Run the main function
    asyncio.run(main(
        args.url,
        args.output_dir,
        args.keywords,
        args.max_depth,
        args.max_pages,
        args.include_external
    ))