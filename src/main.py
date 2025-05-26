"""
Main script for the API documentation crawler.

This script demonstrates how to use the API documentation crawler.
"""

import asyncio
import argparse
from typing import Optional

from .config import CrawlerConfig, LLMConfig, FilterLLMConfig
from .api_doc_crawler import ApiDocCrawler


async def main(url: str, output_dir: str = "output", keywords: Optional[str] = None,
               max_depth: int = 2, max_pages: int = 25, include_external: bool = False,
               target_topic: Optional[str] = None, enable_filtering: bool = False) -> None:
    """
    Main function for the API documentation crawler.
    
    Args:
        url: URL of the API documentation
        output_dir: Directory to save the results in
        keywords: Comma-separated list of keywords for relevance scoring
        max_depth: Maximum depth for crawling
        max_pages: Maximum number of pages to crawl
        include_external: Whether to include external links
        target_topic: Target topic for LLM-based binary filtering (e.g., "Python SDK documentation")
        enable_filtering: Whether to enable LLM-based filtering (requires target_topic)
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
    
    # Create filter LLM config only if filtering is explicitly enabled
    filter_llm_config = None
    if enable_filtering and target_topic:
        filter_llm_config = FilterLLMConfig()
    
    # Create the crawler with dual-model configuration (deduplication always enabled)
    crawler = ApiDocCrawler(crawler_config, llm_config, filter_llm_config, target_topic or "", enable_filtering)
    
    # Crawl and parse with optional filtering
    results = await crawler.crawl_and_parse(url)
    
    # Save results
    crawler.save_results(results, output_dir)
    
    print(f"Processed {len(results)} pages from {url}")
    
    if enable_filtering and target_topic:
        print(f"Used LLM binary filtering for target topic: {target_topic}")
    else:
        print("No filtering applied - all crawled pages were kept")
    
    print("Content-based deduplication enabled - avoided redundant LLM processing")


if __name__ == "__main__":
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="API Documentation Crawler")
    parser.add_argument("url", help="URL of the API documentation")
    parser.add_argument("--output-dir", default="output", help="Directory to save the results in")
    parser.add_argument("--keywords", help="Comma-separated list of keywords for relevance scoring")
    parser.add_argument("--max-depth", type=int, default=2, help="Maximum depth for crawling")
    parser.add_argument("--max-pages", type=int, default=25, help="Maximum number of pages to crawl")
    parser.add_argument("--include-external", action="store_true", help="Include external links")
    parser.add_argument("--enable-filtering", action="store_true", help="Enable LLM-based page filtering for relevance (must be used with --target-topic)")
    parser.add_argument("--target-topic", help="Target topic for filtering when --enable-filtering is used (e.g., 'Python SDK documentation')")
    
    args = parser.parse_args()
    
    # Validate flag combination
    if args.enable_filtering and not args.target_topic:
        parser.error("--target-topic is required when --enable-filtering is used")
    
    # Run the main function
    asyncio.run(main(
        args.url,
        args.output_dir,
        args.keywords,
        args.max_depth,
        args.max_pages,
        args.include_external,
        args.target_topic,
        args.enable_filtering
    ))