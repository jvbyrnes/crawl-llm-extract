#!/usr/bin/env python3
"""
Test script for content-based deduplication functionality.

This script demonstrates how the deduplication system works by:
1. Running the crawler twice on the same URL
2. Showing cache hits on the second run
3. Displaying cache statistics
"""

import asyncio
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.config import CrawlerConfig, LLMConfig
from src.api_doc_crawler import ApiDocCrawler


async def test_deduplication():
    """Test the content deduplication functionality."""
    
    print("=" * 60)
    print("CONTENT DEDUPLICATION TEST")
    print("=" * 60)
    
    # Test URL (using a simple test page)
    test_url = "https://httpbin.org/html"
    
    # Create configurations
    crawler_config = CrawlerConfig(max_depth=1, max_pages=5)
    llm_config = LLMConfig()
    
    print(f"\nTest URL: {test_url}")
    print(f"Max pages: {crawler_config.max_pages}")
    print(f"Max depth: {crawler_config.max_depth}")
    
    # First run - should process everything with LLM
    print("\n" + "=" * 40)
    print("FIRST RUN (Fresh cache)")
    print("=" * 40)
    
    crawler1 = ApiDocCrawler(
        crawler_config=crawler_config,
        llm_config=llm_config
    )
    
    # Show initial cache stats
    initial_stats = crawler1.get_cache_stats()
    print(f"\nInitial cache stats: {initial_stats}")
    
    results1 = await crawler1.crawl_and_parse(test_url)
    
    print(f"\nFirst run completed:")
    print(f"  Processed {len(results1)} pages")
    
    # Show cache stats after first run
    after_first_stats = crawler1.get_cache_stats()
    print(f"\nCache stats after first run: {after_first_stats}")
    
    # Second run - should use cached results
    print("\n" + "=" * 40)
    print("SECOND RUN (Should use cache)")
    print("=" * 40)
    
    crawler2 = ApiDocCrawler(
        crawler_config=crawler_config,
        llm_config=llm_config
    )
    
    results2 = await crawler2.crawl_and_parse(test_url)
    
    print(f"\nSecond run completed:")
    print(f"  Processed {len(results2)} pages")
    
    # Analyze results
    print("\n" + "=" * 40)
    print("RESULTS ANALYSIS")
    print("=" * 40)
    
    cached_count = sum(1 for r in results2 if r.get('cached', False))
    new_count = len(results2) - cached_count
    
    print(f"\nSecond run breakdown:")
    print(f"  Total pages: {len(results2)}")
    print(f"  Cached pages: {cached_count}")
    print(f"  Newly processed: {new_count}")
    print(f"  Cache hit rate: {cached_count/len(results2)*100:.1f}%" if len(results2) > 0 else "  Cache hit rate: 0%")
    
    # Show detailed comparison
    print(f"\nDetailed comparison:")
    for i, (r1, r2) in enumerate(zip(results1, results2)):
        print(f"  Page {i+1}: {r1['url']}")
        print(f"    First run:  LLM processed")
        print(f"    Second run: {'Cached' if r2.get('cached') else 'LLM processed'}")
        if r2.get('cached') and r2.get('cache_timestamp'):
            print(f"    Cache time: {r2['cache_timestamp']}")
    
    
    # Final cache stats
    final_stats = crawler1.get_cache_stats()
    print(f"\nFinal cache stats: {final_stats}")
    
    print("\n" + "=" * 60)
    print("TEST COMPLETED")
    print("=" * 60)
    print("\nKey observations:")
    print("1. First run processes all pages with LLM")
    print("2. Second run uses cached results (no redundant LLM calls)")
    print("3. Deduplication is always enabled to optimize performance and cost")
    print("4. Cache statistics show total URLs and files tracked")


async def test_cache_management():
    """Test cache management functionality."""
    
    print("\n" + "=" * 60)
    print("CACHE MANAGEMENT TEST")
    print("=" * 60)
    
    crawler = ApiDocCrawler()
    
    # Show cache stats
    stats = crawler.get_cache_stats()
    print(f"\nCurrent cache statistics:")
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    # Clean up stale entries
    print(f"\nCleaning up stale cache entries...")
    removed = crawler.cleanup_cache()
    print(f"Removed {removed} stale entries")
    
    # Show updated stats
    updated_stats = crawler.get_cache_stats()
    print(f"\nUpdated cache statistics:")
    for key, value in updated_stats.items():
        print(f"  {key}: {value}")


if __name__ == "__main__":
    print("Starting content deduplication tests...")
    print("Note: This test requires valid LLM configuration in your .env file")
    
    try:
        # Run deduplication test
        asyncio.run(test_deduplication())
        
        # Run cache management test
        asyncio.run(test_cache_management())
        
    except KeyboardInterrupt:
        print("\nTest interrupted by user")
    except Exception as e:
        print(f"\nTest failed with error: {e}")
        print("Make sure you have:")
        print("1. Valid .env file with LLM configuration")
        print("2. Internet connection for test URL")
        print("3. All required dependencies installed")