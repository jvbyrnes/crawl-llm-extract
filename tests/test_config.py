"""
Tests for the configuration classes.
"""

import unittest
import sys
import os

# Add the src directory to the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.config import CrawlerConfig, LLMConfig


class TestCrawlerConfig(unittest.TestCase):
    """
    Tests for the CrawlerConfig class.
    """
    
    def test_default_values(self):
        """Test that default values are set correctly."""
        config = CrawlerConfig()
        self.assertEqual(config.max_depth, 2)
        self.assertEqual(config.include_external, False)
        self.assertEqual(config.max_pages, 25)
        self.assertEqual(config.keywords, [])
        self.assertEqual(config.weight, 0.7)
    
    def test_custom_values(self):
        """Test that custom values are set correctly."""
        config = CrawlerConfig(max_depth=3, include_external=True, max_pages=50)
        self.assertEqual(config.max_depth, 3)
        self.assertEqual(config.include_external, True)
        self.assertEqual(config.max_pages, 50)
    
    def test_set_keywords(self):
        """Test that keywords are set correctly."""
        config = CrawlerConfig()
        config.set_keywords(["test", "keywords"], 0.8)
        self.assertEqual(config.keywords, ["test", "keywords"])
        self.assertEqual(config.weight, 0.8)
    
    def test_validation_success(self):
        """Test that validation succeeds for valid values."""
        config = CrawlerConfig(max_depth=3, include_external=True, max_pages=50)
        try:
            config.validate()
        except ValueError:
            self.fail("validate() raised ValueError unexpectedly!")
    
    def test_validation_failure(self):
        """Test that validation fails for invalid values."""
        config = CrawlerConfig(max_depth=0)
        with self.assertRaises(ValueError):
            config.validate()
        
        config = CrawlerConfig(max_pages=0)
        with self.assertRaises(ValueError):
            config.validate()
        
        config = CrawlerConfig()
        config.weight = 1.5
        with self.assertRaises(ValueError):
            config.validate()


class TestLLMConfig(unittest.TestCase):
    """
    Tests for the LLMConfig class.
    """
    
    def test_default_values(self):
        """Test that default values are set correctly."""
        config = LLMConfig()
        self.assertEqual(config.provider, "openai/gpt-4o")
        self.assertEqual(config.temperature, 0.1)
        self.assertIsNotNone(config.instruction)
    
    def test_custom_values(self):
        """Test that custom values are set correctly."""
        config = LLMConfig(provider="anthropic/claude-3", temperature=0.5)
        self.assertEqual(config.provider, "anthropic/claude-3")
        self.assertEqual(config.temperature, 0.5)
    
    def test_set_custom_instruction(self):
        """Test that custom instruction is set correctly."""
        config = LLMConfig()
        custom_instruction = "This is a custom instruction."
        config.set_custom_instruction(custom_instruction)
        self.assertEqual(config.instruction, custom_instruction)
    
    def test_validation_success(self):
        """Test that validation succeeds for valid values."""
        config = LLMConfig(provider="anthropic/claude-3", temperature=0.5)
        try:
            config.validate()
        except ValueError:
            self.fail("validate() raised ValueError unexpectedly!")
    
    def test_validation_failure(self):
        """Test that validation fails for invalid values."""
        config = LLMConfig(provider="")
        with self.assertRaises(ValueError):
            config.validate()
        
        config = LLMConfig(temperature=1.5)
        with self.assertRaises(ValueError):
            config.validate()
        
        config = LLMConfig()
        config.instruction = ""
        with self.assertRaises(ValueError):
            config.validate()


if __name__ == "__main__":
    unittest.main()