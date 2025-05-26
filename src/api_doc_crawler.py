"""
API Documentation Crawler module.

This module implements the high-level orchestrator that coordinates the crawling and parsing process.
"""

import os
import asyncio
from typing import List, Dict, Any, Optional
import json
from datetime import datetime, timezone

from .config import CrawlerConfig, LLMConfig, FilterLLMConfig
from .deep_crawler import DeepCrawler
from .llm_parser import LLMParser
from .url_filter import URLFilter
from .content_index import ContentIndexManager


class ApiDocCrawler:
    """
    High-level orchestrator that coordinates the crawling and parsing process.
    Simplified to focus on core functionality.
    """
    
    def __init__(self, crawler_config: Optional[CrawlerConfig] = None,
                 llm_config: Optional[LLMConfig] = None,
                 filter_llm_config: Optional[FilterLLMConfig] = None,
                 target_topic: str = "",
                 filtering_enabled: bool = False):
        """
        Initialize with optional configurations for dual-model architecture.
        Content-based deduplication is always enabled to avoid redundant LLM processing.
        
        Args:
            crawler_config: Configuration for the crawler (CrawlerConfig)
            llm_config: Configuration for the extraction LLM (LLMConfig)
            filter_llm_config: Configuration for the filtering LLM (FilterLLMConfig)
            target_topic: Target topic for URL filtering (e.g., "Python SDK documentation")
            filtering_enabled: Whether to enable LLM-based filtering
        """
        self.crawler_config = crawler_config or CrawlerConfig()
        self.llm_config = llm_config or LLMConfig()
        self.filter_llm_config = filter_llm_config
        self.target_topic = target_topic
        self.filtering_enabled = filtering_enabled
        self.deep_crawler = DeepCrawler(self.crawler_config)
        self.llm_parser = LLMParser(self.llm_config)
        
        # Initialize content index manager (always enabled for deduplication)
        self.content_index = ContentIndexManager()
        
        # Only initialize URLFilter when filtering is enabled
        if filtering_enabled and filter_llm_config:
            self.url_filter = URLFilter(filter_llm_config, target_topic)
        else:
            self.url_filter = None
    
    async def crawl_and_parse(self, url: str) -> List[Dict[str, Any]]:
        """
        Crawl the API documentation, filter for inclusion, and parse the content with deduplication.
        
        Args:
            url: URL of the API documentation
            
        Returns:
            Processed results (mix of newly processed and cached content)
        """
        # Crawl the URL
        print(f"Crawling {url}...")
        crawler_results = await self.deep_crawler.crawl(url)
        
        if not crawler_results:
            print("No results found during crawling.")
            return []
        
        print(f"Found {len(crawler_results)} pages.")
        
        # Filter results for inclusion if filtering is explicitly enabled
        if self.filtering_enabled and self.target_topic and self.url_filter:
            print(f"Filtering for inclusion based on: {self.target_topic}")
            crawler_results = await self.url_filter.filter_crawled_results(crawler_results)
            
            if not crawler_results:
                print("No pages included after filtering.")
                return []
            
            print(f"After filtering: {len(crawler_results)} included pages.")
        else:
            print("Filtering disabled - keeping all crawled pages.")
        
        # Process each result with content deduplication
        parsed_results = []
        cache_hits = 0
        llm_processed = 0
        
        for i, result in enumerate(crawler_results):
            page_url = result['url']
            cleaned_html = result['cleaned_html']
            
            print(f"Processing page {i+1}/{len(crawler_results)}: {page_url}")
            
            try:
                # Check if we should process with LLM or use cached result
                should_process, reason = self.content_index.should_process_with_llm(page_url, cleaned_html)
                print(f"  Deduplication check: {reason}")
                
                if not should_process:
                    # Use cached extraction
                    cached_extraction = self.content_index.get_cached_extraction(page_url)
                    cached_metadata = self.content_index.get_cached_metadata(page_url)
                    
                    if cached_extraction and cached_metadata:
                        parsed_result = {
                            'url': page_url,
                            'title': cached_metadata.get('title', result.get('title')),
                            'depth': cached_metadata.get('depth', result.get('depth')),
                            'content': cached_extraction.get('content', []),
                            'cached': True,
                            'cache_timestamp': cached_extraction.get('extraction_timestamp')
                        }
                        
                        # Include filtering metadata if available
                        if 'included' in result:
                            parsed_result['included'] = result['included']
                            parsed_result['decision_explanation'] = result['decision_explanation']
                        elif 'included' in cached_metadata:
                            parsed_result['included'] = cached_metadata['included']
                            parsed_result['decision_explanation'] = cached_metadata.get('decision_explanation', '')
                        
                        parsed_results.append(parsed_result)
                        cache_hits += 1
                        print(f"  Used cached extraction from {cached_extraction.get('extraction_timestamp', 'unknown time')}")
                        continue
                    else:
                        print(f"  Warning: Cache entry exists but files missing, will re-process")
                
                # Process with LLM (either deduplication disabled or content changed)
                parsed_content = await self.llm_parser.parse(cleaned_html)
                
                parsed_result = {
                    'url': page_url,
                    'title': result['title'],
                    'depth': result['depth'],
                    'content': parsed_content,
                    'cached': False,
                    'extraction_timestamp': datetime.now(timezone.utc).isoformat()
                }
                
                # Include decision metadata if available
                if 'included' in result:
                    parsed_result['included'] = result['included']
                    parsed_result['decision_explanation'] = result['decision_explanation']
                
                parsed_results.append(parsed_result)
                llm_processed += 1
                
                # Update content index with new extraction
                content_hash = self.content_index.calculate_content_hash(cleaned_html)
                
                extraction_data = {
                    'url': page_url,
                    'content': parsed_content,
                    'extraction_timestamp': parsed_result['extraction_timestamp']
                }
                
                metadata = {
                    'url': page_url,
                    'title': result['title'],
                    'depth': result['depth'],
                    'crawl_timestamp': datetime.now(timezone.utc).isoformat()
                }
                
                # Include filtering metadata if available
                if 'included' in result:
                    metadata['included'] = result['included']
                    metadata['decision_explanation'] = result['decision_explanation']
                
                self.content_index.update_url_record(page_url, content_hash, extraction_data, metadata)
                
                print(f"  Successfully processed with LLM")
                
            except Exception as e:
                print(f"  Error processing {page_url}: {e}")
        
        # Print deduplication statistics
        total_pages = len(crawler_results)
        print(f"\nDeduplication Summary:")
        print(f"  Total pages: {total_pages}")
        print(f"  Cache hits: {cache_hits}")
        print(f"  LLM processed: {llm_processed}")
        print(f"  Cache hit rate: {cache_hits/total_pages*100:.1f}%" if total_pages > 0 else "  Cache hit rate: 0%")
        
        return parsed_results
    
    async def crawl_only(self, url: str) -> List[Dict[str, Any]]:
        """
        Only crawl the API documentation without parsing, with optional filtering.
        
        Args:
            url: URL of the API documentation
            
        Returns:
            Crawled results (filtered if target topic is specified)
        """
        crawler_results = await self.deep_crawler.crawl(url)
        
        # Filter results for inclusion if filtering is explicitly enabled
        if self.filtering_enabled and self.target_topic and self.url_filter and crawler_results:
            print(f"Filtering crawled results for inclusion based on: {self.target_topic}")
            crawler_results = await self.url_filter.filter_crawled_results(crawler_results)
        elif crawler_results:
            print("Filtering disabled - keeping all crawled pages.")
        
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
        if self.url_filter:
            self.url_filter.set_target_topic(target_topic)
        print(f"Updated target topic to: {target_topic}")
    
    def set_filter_llm_config(self, filter_llm_config: FilterLLMConfig):
        """
        Set or update the filter LLM configuration.
        
        Args:
            filter_llm_config: New filter LLM configuration
        """
        self.filter_llm_config = filter_llm_config
        if self.filtering_enabled:
            self.url_filter = URLFilter(filter_llm_config, self.target_topic)
        print(f"Updated filter LLM config to: {filter_llm_config}")
    
    def save_results(self, results: List[Dict[str, Any]], output_dir: str = "output") -> None:
        """
        Save the results to files in the output directory.
        
        Args:
            results: Results to save (mix of cached and newly processed)
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
            
            # Save the metadata as JSON (including cache and decision info)
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
                        'filename': f"page_{i+1}.md",
                        'cached': r.get('cached', False)
                    }
                    
                    # Include timestamps
                    if r.get('cached') and r.get('cache_timestamp'):
                        entry['cache_timestamp'] = r['cache_timestamp']
                    elif r.get('extraction_timestamp'):
                        entry['extraction_timestamp'] = r['extraction_timestamp']
                    
                    # Include decision info if available
                    if 'included' in r:
                        entry['included'] = r['included']
                        entry['decision_explanation'] = r.get('decision_explanation', '')
                    
                    index.append(entry)
            json.dump(index, f, indent=2)
        
        # Print summary with cache statistics
        total_results = len(results)
        cached_results = sum(1 for r in results if r.get('cached', False))
        new_results = total_results - cached_results
        
        print(f"Results saved to {output_dir}")
        print(f"  Total: {total_results} pages")
        print(f"  Cached: {cached_results} pages")
        print(f"  Newly processed: {new_results} pages")
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """
        Get content cache statistics.
        
        Returns:
            Dictionary containing cache statistics, or empty dict if deduplication disabled
        """
        stats = self.content_index.get_cache_stats()
        stats['deduplication_enabled'] = True
        return stats
    
    def cleanup_cache(self) -> int:
        """
        Clean up stale cache entries.
        
        Returns:
            Number of stale entries removed, or 0 if deduplication disabled
        """
        return self.content_index.cleanup_stale_entries()