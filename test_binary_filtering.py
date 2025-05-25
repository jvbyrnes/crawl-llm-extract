#!/usr/bin/env python3
"""
Test script to verify binary URL filtering functionality.

This script demonstrates the new binary include/exclude filtering system
that replaces the previous relevancy scoring approach.
"""

import asyncio
import os
from src.config import CrawlerConfig, LLMConfig, FilterLLMConfig
from src.api_doc_crawler import ApiDocCrawler

async def test_binary_filtering():
    """
    Test the binary filtering functionality with a simple example.
    """
    print("🧪 Testing Binary URL Filtering System")
    print("=" * 50)
    
    # Check if environment variables are set
    if not os.getenv('FILTER_LLM_PROVIDER'):
        print("❌ FILTER_LLM_PROVIDER environment variable not set")
        print("Please set up your .env file with the required LLM configuration")
        return
    
    # Create configurations
    crawler_config = CrawlerConfig(
        max_depth=1,  # Keep it simple for testing
        max_pages=5,  # Limit pages for quick test
        include_external=False
    )
    
    llm_config = LLMConfig()
    filter_llm_config = FilterLLMConfig()
    
    # Test target topic
    target_topic = "Python SDK documentation"
    
    print(f"🎯 Target Topic: {target_topic}")
    print(f"📊 Max Pages: {crawler_config.max_pages}")
    print(f"🔍 Max Depth: {crawler_config.max_depth}")
    print()
    
    # Create crawler with binary filtering
    crawler = ApiDocCrawler(
        crawler_config=crawler_config,
        llm_config=llm_config,
        filter_llm_config=filter_llm_config,
        target_topic=target_topic
    )
    
    # Test URL (using a documentation site)
    test_url = "https://docs.python.org/3/library/"
    
    print(f"🌐 Testing URL: {test_url}")
    print()
    
    try:
        # Test crawl_only method (no parsing, just filtering)
        print("🔄 Testing crawl_only with binary filtering...")
        crawl_results = await crawler.crawl_only(test_url)
        
        print(f"✅ Crawl completed!")
        print(f"📄 Pages after binary filtering: {len(crawl_results)}")
        
        # Display results
        if crawl_results:
            print("\n📋 Filtered Results:")
            for i, result in enumerate(crawl_results[:3]):  # Show first 3 results
                included = result.get('included', 'Unknown')
                explanation = result.get('decision_explanation', 'No explanation')
                print(f"  {i+1}. {result['url']}")
                print(f"     ✅ Included: {included}")
                print(f"     💭 Reason: {explanation[:100]}...")
                print()
        
        # Test the new binary decision format
        print("🔍 Verifying Binary Decision Format:")
        for result in crawl_results[:2]:
            if 'included' in result:
                print(f"  ✅ Found 'included' field: {result['included']}")
            if 'decision_explanation' in result:
                print(f"  ✅ Found 'decision_explanation' field")
            
            # Verify old scoring fields are NOT present
            if 'relevance_score' in result:
                print(f"  ❌ ERROR: Old 'relevance_score' field still present!")
            if 'relevance_explanation' in result:
                print(f"  ❌ ERROR: Old 'relevance_explanation' field still present!")
        
        print("\n🎉 Binary filtering test completed successfully!")
        print(f"📊 Summary: {len(crawl_results)} pages included based on binary decisions")
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()

def main():
    """
    Main function to run the binary filtering test.
    """
    print("Binary URL Filtering Test")
    print("This test verifies the new include/exclude decision system")
    print()
    
    # Run the async test
    asyncio.run(test_binary_filtering())

if __name__ == "__main__":
    main()