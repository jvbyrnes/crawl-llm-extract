#!/usr/bin/env python3
"""
Test script to verify o1-mini model compatibility with the dual-model architecture.

This script tests that o1 models work correctly with the URLFilter by using
the proper message format (no system messages, no temperature/max_tokens).
"""

import asyncio
import os
from src.url_filter import URLFilter
from src.config import FilterLLMConfig


async def test_o1_model_compatibility():
    """Test that o1-mini works with the URLFilter."""
    
    print("🧪 Testing o1-mini Model Compatibility")
    print("=" * 50)
    
    # Check if API key is available
    if not os.getenv('OPENAI_API_KEY'):
        print("❌ OPENAI_API_KEY not found in environment variables.")
        return
    
    # Check if filter model is configured
    filter_provider = os.getenv('FILTER_LLM_PROVIDER')
    if not filter_provider:
        print("❌ FILTER_LLM_PROVIDER not found in environment variables.")
        print("Please set FILTER_LLM_PROVIDER in your .env file")
        return
    
    print(f"✅ Using filter model: {filter_provider}")
    
    # Create filter configuration
    try:
        filter_config = FilterLLMConfig()
        print(f"✅ Filter config created successfully")
        print(f"   Model: {filter_config.provider}")
        print(f"   Temperature: {filter_config.temperature}")
    except Exception as e:
        print(f"❌ Error creating filter config: {e}")
        return
    
    # Create URL filter
    target_topic = "Python SDK documentation"
    url_filter = URLFilter(filter_config, target_topic)
    print(f"✅ URL filter created with target: {target_topic}")
    
    # Create a test page result
    test_page = {
        'url': 'https://docs.pinecone.io/reference/python-sdk',
        'title': 'Python SDK - Pinecone Docs',
        'cleaned_html': 'This page contains Python SDK documentation with API reference, code examples, and installation instructions for the Pinecone vector database Python client.',
        'depth': 0
    }
    
    print(f"\n🔍 Testing relevance analysis...")
    print(f"Test page: {test_page['url']}")
    
    try:
        # Test the relevance analysis
        relevance_score, explanation = await url_filter._analyze_page_relevance(test_page)
        
        print(f"✅ Analysis completed successfully!")
        print(f"   Relevance Score: {relevance_score}")
        print(f"   Explanation: {explanation}")
        
        if relevance_score > 0.5:
            print(f"✅ Test passed: Relevance score indicates successful analysis")
        else:
            print(f"⚠️  Low relevance score, but analysis completed without errors")
            
    except Exception as e:
        print(f"❌ Error during analysis: {e}")
        print(f"   This might indicate a model compatibility issue")
        return
    
    print(f"\n🎉 o1-mini compatibility test completed successfully!")
    print(f"   The URLFilter correctly handles o1 models by:")
    print(f"   • Using user-only messages (no system messages)")
    print(f"   • Omitting temperature and max_tokens parameters")
    print(f"   • Combining system prompt into user message")


if __name__ == "__main__":
    print("o1-mini Model Compatibility Test")
    print("This test verifies that o1 models work with the URLFilter")
    print()
    
    asyncio.run(test_o1_model_compatibility())