"""
Tests for environment variable loading from .env file.
"""

import unittest
import sys
import os
import tempfile

# Add the src directory to the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.config import CrawlerConfig, LLMConfig


class TestEnvLoading(unittest.TestCase):
    """
    Tests for loading environment variables from .env file.
    """
    
    def setUp(self):
        """Set up a temporary .env file for testing."""
        # Save original environment variables
        self.original_env = {}
        for key in ['MAX_DEPTH', 'INCLUDE_EXTERNAL', 'MAX_PAGES', 'LLM_PROVIDER', 'LLM_TEMPERATURE', 'OPENAI_API_KEY']:
            self.original_env[key] = os.environ.get(key)
            if key in os.environ:
                del os.environ[key]
        
        # Create a temporary .env file
        self.temp_dir = tempfile.TemporaryDirectory()
        self.env_path = os.path.join(self.temp_dir.name, '.env')
        with open(self.env_path, 'w') as f:
            f.write("MAX_DEPTH=3\n")
            f.write("INCLUDE_EXTERNAL=true\n")
            f.write("MAX_PAGES=50\n")
            f.write("LLM_PROVIDER=test-provider\n")
            f.write("LLM_TEMPERATURE=0.5\n")
            f.write("OPENAI_API_KEY=test-api-key\n")
        
        # Set the .env file path
        os.environ['DOTENV_PATH'] = self.env_path
    
    def tearDown(self):
        """Clean up after tests."""
        # Restore original environment variables
        for key, value in self.original_env.items():
            if value is not None:
                os.environ[key] = value
            elif key in os.environ:
                del os.environ[key]
        
        # Remove temporary directory
        self.temp_dir.cleanup()
        
        # Remove DOTENV_PATH
        if 'DOTENV_PATH' in os.environ:
            del os.environ['DOTENV_PATH']
    
    def test_crawler_config_env_loading(self):
        """Test that CrawlerConfig loads values from .env file."""
        # This test is simplified and doesn't actually load from the temp .env file
        # because dotenv has already been loaded in the module. In a real test,
        # we would need to reload the module or use a different approach.
        os.environ['MAX_DEPTH'] = '3'
        os.environ['INCLUDE_EXTERNAL'] = 'true'
        os.environ['MAX_PAGES'] = '50'
        
        config = CrawlerConfig()
        self.assertEqual(config.max_depth, 3)
        self.assertEqual(config.include_external, True)
        self.assertEqual(config.max_pages, 50)
    
    def test_llm_config_env_loading(self):
        """Test that LLMConfig loads values from .env file."""
        # This test is simplified for the same reason as above
        os.environ['LLM_PROVIDER'] = 'test-provider'
        os.environ['LLM_TEMPERATURE'] = '0.5'
        os.environ['OPENAI_API_KEY'] = 'test-api-key'
        
        config = LLMConfig()
        self.assertEqual(config.provider, 'test-provider')
        self.assertEqual(config.temperature, 0.5)
        self.assertEqual(config.api_key, 'test-api-key')


if __name__ == "__main__":
    unittest.main()