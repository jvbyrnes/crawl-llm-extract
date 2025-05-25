"""
Configuration classes for the API documentation crawler.

This module contains the configuration classes for the crawler and LLM parser.
"""

import os
from typing import List, Optional
from dotenv import load_dotenv

# Load environment variables from .env file
# Allow specifying a custom .env file path through DOTENV_PATH
dotenv_path = os.getenv('DOTENV_PATH', '.env')
load_dotenv(dotenv_path)

class CrawlerConfig:
    """
    Configuration for the web crawler used in API documentation crawling.
    Keeps it simple with just the essential parameters.
    """
    
    def __init__(self, max_depth=None, include_external=None, max_pages=None):
        """
        Initialize with basic crawler parameters.
        
        Args:
            max_depth: Maximum depth for crawling
            include_external: Whether to include external links
            max_pages: Maximum number of pages to crawl
        """
        # Load from environment variables or use defaults
        self.max_depth = max_depth if max_depth is not None else self._get_env_int('MAX_DEPTH', 2)
        self.include_external = include_external if include_external is not None else self._get_env_bool('INCLUDE_EXTERNAL', False)
        self.max_pages = max_pages if max_pages is not None else self._get_env_int('MAX_PAGES', 25)
        self.keywords = []
        self.weight = self._get_env_float('KEYWORD_WEIGHT', 0.7)
    
    def _get_env_int(self, key: str, default: int) -> int:
        """Get an integer from environment variables."""
        value = os.getenv(key)
        return int(value) if value is not None else default
    
    def _get_env_bool(self, key: str, default: bool) -> bool:
        """Get a boolean from environment variables."""
        value = os.getenv(key)
        if value is None:
            return default
        return value.lower() in ('true', 'yes', '1', 't', 'y')
    
    def _get_env_float(self, key: str, default: float) -> float:
        """Get a float from environment variables."""
        value = os.getenv(key)
        return float(value) if value is not None else default
    
    def set_keywords(self, keywords, weight=0.7):
        """
        Set keywords for the KeywordRelevanceScorer.
        
        Args:
            keywords: List of keywords for scoring
            weight: Weight for the scorer
        """
        self.keywords = keywords
        self.weight = weight
        
    def validate(self):
        """
        Validate the configuration parameters.
        
        Raises:
            ValueError: If any parameter is invalid
        """
        if self.max_depth < 1:
            raise ValueError("max_depth must be at least 1")
        if self.max_pages < 1:
            raise ValueError("max_pages must be at least 1")
        if self.weight < 0 or self.weight > 1:
            raise ValueError("weight must be between 0 and 1")
        
    def __str__(self):
        """
        Return a string representation of the configuration.
        
        Returns:
            String representation
        """
        return (f"CrawlerConfig(max_depth={self.max_depth}, "
                f"include_external={self.include_external}, "
                f"max_pages={self.max_pages}, "
                f"keywords={self.keywords}, "
                f"weight={self.weight})")


class LLMConfig:
    """
    Configuration for the LLM used in parsing API documentation.
    Keeps it simple with just the essential parameters.
    """
    
    def __init__(self, provider=None, temperature=None):
        """
        Initialize with provider and temperature.
        
        Args:
            provider: The LLM provider and model to use
            temperature: The temperature setting for the LLM (0.0-1.0)
        """
        # Load from environment variables or use defaults
        self.provider = provider if provider is not None else os.getenv('LLM_PROVIDER', 'openai/gpt-4o')
        self.temperature = temperature if temperature is not None else self._get_env_float('LLM_TEMPERATURE', 0.1)
        self.api_key = os.getenv('OPENAI_API_KEY')
        self.instruction = self.get_generic_instruction()
    
    def _get_env_float(self, key: str, default: float) -> float:
        """Get a float from environment variables."""
        value = os.getenv(key)
        return float(value) if value is not None else default
    
    def get_generic_instruction(self):
        """
        Get the generic instruction for extracting information from API documentation.
        
        Returns:
            Generic instruction for API documentation extraction
        """
        return """
        Extract the complete API documentation information while preserving its original structure and content.
        
        Focus on extracting:
        1. All function and method definitions with their complete signatures
        2. All parameters, their types, and descriptions
        3. Return values and their types
        4. Class and object definitions with their properties and methods
        5. Code examples and usage patterns
        6. Important notes, warnings, and best practices
        7. Any authentication or configuration requirements
        
        Format the output as clean markdown with:
        - Code blocks for all code examples with appropriate syntax highlighting
        - Function/method signatures in their own code blocks
        - Clear hierarchical headers for organization
        - Tables for parameter descriptions where appropriate
        - Preserved original structure and terminology
        
        Exclude only clearly irrelevant elements like:
        - Navigation menus and breadcrumbs
        - Search bars and version selectors
        - Footer content unrelated to the API
        - Advertisements or promotional content
        - UI elements that don't contribute to understanding the API
        
        The goal is to create a comprehensive, well-structured representation of the API
        that preserves all technical details regardless of the programming language or API type.
        """
    
    def set_custom_instruction(self, instruction):
        """
        Set a custom instruction for the LLM.
        
        Args:
            instruction: Custom instruction for the LLM
        """
        self.instruction = instruction
        
    def validate(self):
        """
        Validate the configuration parameters.
        
        Raises:
            ValueError: If any parameter is invalid
        """
        if not self.provider:
            raise ValueError("provider must not be empty")
        if self.temperature < 0 or self.temperature > 1:
            raise ValueError("temperature must be between 0 and 1")
        if not self.instruction:
            raise ValueError("instruction must not be empty")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY not set in environment variables or .env file")
        
    def __str__(self):
        """
        Return a string representation of the configuration.
        
        Returns:
            String representation
        """
        instruction_preview = self.instruction[:50] + "..." if self.instruction else "None"
        return (f"LLMConfig(provider={self.provider}, "
                f"temperature={self.temperature}, "
                f"instruction={instruction_preview})")


class FilterLLMConfig:
    """
    Configuration for the LLM used in URL relevance filtering.
    Separate from extraction LLM to allow different models and optimization.
    """
    
    def __init__(self, provider=None, temperature=None):
        """
        Initialize with provider and temperature for filtering tasks.
        
        Args:
            provider: The LLM provider and model to use for filtering
            temperature: The temperature setting for the LLM (0.0-1.0)
        """
        # Load from environment variables - REQUIRED for filtering
        self.provider = provider if provider is not None else os.getenv('FILTER_LLM_PROVIDER')
        self.temperature = temperature if temperature is not None else self._get_env_float('FILTER_LLM_TEMPERATURE', 0.0)
        self.api_key = os.getenv('OPENAI_API_KEY')  # For now, assume OpenAI for both
    
    def _get_env_float(self, key: str, default: float) -> float:
        """Get a float from environment variables."""
        value = os.getenv(key)
        return float(value) if value is not None else default
    
    def validate(self):
        """
        Validate the configuration parameters.
        
        Raises:
            ValueError: If any parameter is invalid or missing
        """
        if not self.provider:
            raise ValueError("FILTER_LLM_PROVIDER must be set in environment variables or .env file")
        if self.temperature < 0 or self.temperature > 1:
            raise ValueError("temperature must be between 0 and 1")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY not set in environment variables or .env file")
    
    def __str__(self):
        """
        Return a string representation of the configuration.
        
        Returns:
            String representation
        """
        return (f"FilterLLMConfig(provider={self.provider}, "
                f"temperature={self.temperature})")