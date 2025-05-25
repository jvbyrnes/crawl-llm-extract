"""
LLM Parser module for API documentation parsing.

This module implements the LLM parsing functionality to filter and extract relevant content.
"""

import os
from typing import List, Dict, Any, Optional

from crawl4ai import LLMConfig as Crawl4aiLLMConfig
from crawl4ai.content_filter_strategy import LLMContentFilter

from .config import LLMConfig


class LLMParser:
    """
    Implements LLM parsing functionality to filter and extract relevant content.
    Simplified to focus on core functionality.
    """
    
    def __init__(self, config: Optional[LLMConfig] = None):
        """
        Initialize with optional configuration.
        
        Args:
            config: Configuration for the LLM (LLMConfig)
        """
        self.config = config or LLMConfig()
        self.filter = None
        
    async def parse(self, html_content: str) -> List[str]:
        """
        Parse the HTML content using the configured LLM.
        
        Args:
            html_content: HTML content to parse
            
        Returns:
            Parsed results as a list of markdown content
        """
        # Validate configuration
        self.config.validate()
        
        # Check for API token
        if not self.config.api_key:
            raise ValueError("OPENAI_API_KEY not set in environment variables or .env file")
        
        # Create LLM configuration for crawl4ai
        llm_config = Crawl4aiLLMConfig(
            provider=self.config.provider,
            api_token=self.config.api_key
        )
        
        # Initialize LLM filter
        self.filter = LLMContentFilter(
            llm_config=llm_config,
            instruction=self.config.instruction,
            verbose=True
        )
        
        try:
            # Apply filtering
            filtered_content = self.filter.filter_content(html_content)
            return filtered_content
        except Exception as e:
            # Basic error handling
            print(f"Error during parsing: {e}")
            return []
    
    def show_usage(self) -> Dict[str, Any]:
        """
        Show token usage information.
        
        Returns:
            Dictionary with usage information
        """
        if self.filter:
            self.filter.show_usage()
            # This is a placeholder as the actual usage data structure depends on crawl4ai
            return {"status": "Usage information displayed"}
        return {"status": "No filter initialized yet"}