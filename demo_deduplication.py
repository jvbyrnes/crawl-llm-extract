#!/usr/bin/env python3
"""
Simple demonstration of the content-based deduplication system.

This script shows how the crawler avoids redundant LLM processing by using
content hashes to detect when pages haven't changed.
"""

import asyncio
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.config import CrawlerConfig, LLMConfig
from src.api_doc_crawler import ApiDocCrawler


async def demo():
    """Demonstrate the deduplication system."""
    
    print("🚀 Content-Based Deduplication Demo")
    print("=" * 50)
    
    # Simple test URL
    test_url = "https://httpbin.org/html"
    
    # Create a simple configuration
    crawler_config = CrawlerConfig(max_depth=1, max_pages=3)
    llm_config = LLMConfig()
    
    print(f"📄 Test URL: {test_url}")
    print(f"⚙️  Max pages: {crawler_config.max_pages}")
    
    # First run
    print("\n🔄 First Run (Building cache)")
    print("-" * 30)
    
    crawler = ApiDocCrawler(
        crawler_config=crawler_config,
        llm_config=llm_config
    )
    
    results1 = await crawler.crawl_and_parse(test_url)
    print(f"✅ Processed {len(results1)} pages")
    
    # Second run - should use cache
    print("\n🔄 Second Run (Using cache)")
    print("-" * 30)
    
    results2 = await crawler.crawl_and_parse(test_url)
    
    # Count cached vs new
    cached = sum(1 for r in results2 if r.get('cached', False))
    new = len(results2) - cached
    
    print(f"✅ Total pages: {len(results2)}")
    print(f"💾 From cache: {cached}")
    print(f"🆕 Newly processed: {new}")
    
    if cached > 0:
        print(f"🎉 Success! Avoided {cached} redundant LLM calls")
    else:
        print("⚠️  No cache hits - this might be expected for dynamic content")
    
    # Show cache stats
    stats = crawler.get_cache_stats()
    print(f"\n📊 Cache Statistics:")
    print(f"   Total URLs tracked: {stats.get('total_urls', 0)}")
    print(f"   Extraction files: {stats.get('extraction_files', 0)}")
    print(f"   Metadata files: {stats.get('metadata_files', 0)}")
    
    print(f"\n💡 The extracted-docs/ directory now contains:")
    print(f"   - content_index.json (URL to hash mapping)")
    print(f"   - extractions/ (cached LLM results)")
    print(f"   - metadata/ (page metadata)")
    
    print(f"\n🎯 Key Benefits:")
    print(f"   ✓ Avoids redundant LLM processing")
    print(f"   ✓ Reduces API costs")
    print(f"   ✓ Faster re-crawling")
    print(f"   ✓ Intelligent content change detection")


if __name__ == "__main__":
    print("Starting deduplication demo...")
    print("Note: Requires valid LLM configuration in .env file\n")
    
    try:
        asyncio.run(demo())
    except KeyboardInterrupt:
        print("\n👋 Demo interrupted")
    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
        print("\nTroubleshooting:")
        print("1. Check your .env file has valid LLM configuration")
        print("2. Ensure internet connection for test URL")
        print("3. Verify all dependencies are installed")