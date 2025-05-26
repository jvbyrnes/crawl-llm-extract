"""
Content Index Manager module.

This module implements content-based deduplication to avoid redundant LLM processing
by tracking content changes via hash comparison of cleaned HTML.
"""

import os
import json
import hashlib
from typing import Dict, Any, Optional, Tuple
from datetime import datetime, timezone


class ContentIndexManager:
    """
    Manages the content hash index and extraction cache to avoid redundant LLM processing.
    
    The system works by:
    1. Calculating SHA-256 hashes of cleaned HTML content
    2. Storing hashes and extraction results in extracted-docs/ directory
    3. Comparing new content hashes with stored hashes before LLM processing
    4. Only processing content through LLM when it has actually changed
    """
    
    def __init__(self, base_dir: str = "extracted-docs"):
        """
        Initialize the ContentIndexManager.
        
        Args:
            base_dir: Base directory for storing index and cached extractions
        """
        self.base_dir = base_dir
        self.index_file = os.path.join(base_dir, "content_index.json")
        self.extractions_dir = os.path.join(base_dir, "extractions")
        self.metadata_dir = os.path.join(base_dir, "metadata")
        
        # Create directories if they don't exist
        os.makedirs(self.extractions_dir, exist_ok=True)
        os.makedirs(self.metadata_dir, exist_ok=True)
        
        # Load existing index
        self.index = self.load_index()
    
    def load_index(self) -> Dict[str, Any]:
        """
        Load the content index from file.
        
        Returns:
            Dictionary containing the content index, empty dict if file doesn't exist
        """
        if os.path.exists(self.index_file):
            try:
                with open(self.index_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                print(f"Warning: Could not load content index: {e}")
                print("Starting with empty index.")
                return {}
        return {}
    
    def save_index(self) -> None:
        """
        Save the content index to file.
        """
        try:
            with open(self.index_file, 'w', encoding='utf-8') as f:
                json.dump(self.index, f, indent=2, ensure_ascii=False)
        except IOError as e:
            print(f"Error saving content index: {e}")
    
    def calculate_content_hash(self, cleaned_html: str) -> str:
        """
        Calculate SHA-256 hash of cleaned HTML content.
        
        Args:
            cleaned_html: The cleaned HTML content to hash
            
        Returns:
            SHA-256 hash as hexadecimal string
        """
        return hashlib.sha256(cleaned_html.encode('utf-8')).hexdigest()
    
    def calculate_url_hash(self, url: str) -> str:
        """
        Calculate a hash of the URL for use in filenames.
        
        Args:
            url: The URL to hash
            
        Returns:
            First 12 characters of SHA-256 hash of URL
        """
        return hashlib.sha256(url.encode('utf-8')).hexdigest()[:12]
    
    def get_url_record(self, url: str) -> Optional[Dict[str, Any]]:
        """
        Get stored record for a URL.
        
        Args:
            url: The URL to look up
            
        Returns:
            Dictionary containing URL record, or None if not found
        """
        return self.index.get(url)
    
    def is_content_changed(self, url: str, new_content_hash: str) -> bool:
        """
        Check if content has changed for a URL by comparing hashes.
        
        Args:
            url: The URL to check
            new_content_hash: Hash of the new content
            
        Returns:
            True if content has changed or URL is new, False if unchanged
        """
        record = self.get_url_record(url)
        if not record:
            return True  # New URL, consider it changed
        
        stored_hash = record.get('content_hash')
        return stored_hash != new_content_hash
    
    def get_cached_extraction(self, url: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve cached LLM extraction result for a URL.
        
        Args:
            url: The URL to get cached extraction for
            
        Returns:
            Dictionary containing cached extraction data, or None if not found
        """
        record = self.get_url_record(url)
        if not record:
            return None
        
        extraction_file = record.get('extraction_file')
        if not extraction_file:
            return None
        
        extraction_path = os.path.join(self.base_dir, extraction_file)
        if not os.path.exists(extraction_path):
            print(f"Warning: Extraction file not found: {extraction_path}")
            return None
        
        try:
            with open(extraction_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            print(f"Warning: Could not load cached extraction: {e}")
            return None
    
    def get_cached_metadata(self, url: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve cached metadata for a URL.
        
        Args:
            url: The URL to get cached metadata for
            
        Returns:
            Dictionary containing cached metadata, or None if not found
        """
        record = self.get_url_record(url)
        if not record:
            return None
        
        metadata_file = record.get('metadata_file')
        if not metadata_file:
            return None
        
        metadata_path = os.path.join(self.base_dir, metadata_file)
        if not os.path.exists(metadata_path):
            print(f"Warning: Metadata file not found: {metadata_path}")
            return None
        
        try:
            with open(metadata_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            print(f"Warning: Could not load cached metadata: {e}")
            return None
    
    def update_url_record(self, url: str, content_hash: str, 
                         extraction_data: Optional[Dict[str, Any]] = None,
                         metadata: Optional[Dict[str, Any]] = None) -> None:
        """
        Update or add URL record with new content hash and optional extraction data.
        
        Args:
            url: The URL to update
            content_hash: Hash of the content
            extraction_data: LLM extraction result to cache
            metadata: Page metadata to cache
        """
        url_hash = self.calculate_url_hash(url)
        timestamp = datetime.now(timezone.utc).isoformat()
        
        # Prepare file paths
        extraction_file = f"extractions/{url_hash}.json"
        metadata_file = f"metadata/{url_hash}_meta.json"
        
        # Update index record
        self.index[url] = {
            'content_hash': content_hash,
            'last_extracted': timestamp,
            'extraction_file': extraction_file,
            'metadata_file': metadata_file,
            'url_hash': url_hash
        }
        
        # Save extraction data if provided
        if extraction_data is not None:
            extraction_path = os.path.join(self.base_dir, extraction_file)
            try:
                with open(extraction_path, 'w', encoding='utf-8') as f:
                    json.dump(extraction_data, f, indent=2, ensure_ascii=False)
            except IOError as e:
                print(f"Error saving extraction data: {e}")
        
        # Save metadata if provided
        if metadata is not None:
            metadata_path = os.path.join(self.base_dir, metadata_file)
            try:
                with open(metadata_path, 'w', encoding='utf-8') as f:
                    json.dump(metadata, f, indent=2, ensure_ascii=False)
            except IOError as e:
                print(f"Error saving metadata: {e}")
        
        # Save updated index
        self.save_index()
    
    def should_process_with_llm(self, url: str, cleaned_html: str) -> Tuple[bool, Optional[str]]:
        """
        Determine if content should be processed with LLM based on content changes.
        
        Args:
            url: The URL being processed
            cleaned_html: The cleaned HTML content
            
        Returns:
            Tuple of (should_process, reason)
            - should_process: True if LLM processing is needed
            - reason: Human-readable reason for the decision
        """
        new_content_hash = self.calculate_content_hash(cleaned_html)
        
        if not self.get_url_record(url):
            return True, "New URL - not in index"
        
        if self.is_content_changed(url, new_content_hash):
            return True, "Content has changed since last extraction"
        
        return False, "Content unchanged - using cached extraction"
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the content cache.
        
        Returns:
            Dictionary containing cache statistics
        """
        total_urls = len(self.index)
        
        # Count existing files
        extraction_files = 0
        metadata_files = 0
        
        for record in self.index.values():
            extraction_path = os.path.join(self.base_dir, record.get('extraction_file', ''))
            metadata_path = os.path.join(self.base_dir, record.get('metadata_file', ''))
            
            if os.path.exists(extraction_path):
                extraction_files += 1
            if os.path.exists(metadata_path):
                metadata_files += 1
        
        return {
            'total_urls': total_urls,
            'extraction_files': extraction_files,
            'metadata_files': metadata_files,
            'index_file_exists': os.path.exists(self.index_file),
            'base_directory': self.base_dir
        }
    
    def cleanup_stale_entries(self) -> int:
        """
        Remove index entries that have missing extraction or metadata files.
        
        Returns:
            Number of stale entries removed
        """
        stale_urls = []
        
        for url, record in self.index.items():
            extraction_path = os.path.join(self.base_dir, record.get('extraction_file', ''))
            metadata_path = os.path.join(self.base_dir, record.get('metadata_file', ''))
            
            # Consider entry stale if both files are missing
            if not os.path.exists(extraction_path) and not os.path.exists(metadata_path):
                stale_urls.append(url)
        
        # Remove stale entries
        for url in stale_urls:
            del self.index[url]
        
        if stale_urls:
            self.save_index()
            print(f"Removed {len(stale_urls)} stale entries from index")
        
        return len(stale_urls)