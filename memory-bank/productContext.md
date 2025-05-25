# Product Context

This file provides a high-level overview of the project and the expected product that will be created. Initially it is based upon projectBrief.md (if provided) and all other available project-related information in the working directory. This file is intended to be updated as the project evolves, and should be used to inform all other modes of the project's goals and context.
2025-05-22 21:15:00 - Initial memory bank creation.

*

## Project Goal

* Create a web crawler specifically designed to scrape online programming API documentation (e.g., Pinecone vector database Python SDK documentation).
* Refactor existing example code into modular components for better maintainability and reusability.

## Key Features

* Deep crawling functionality to navigate through API documentation pages
* LLM-based content parsing to extract and filter relevant information from HTML
* Modular architecture with separate components for crawling and parsing

## Overall Architecture

* Uses the `crawl4ai` library for web crawling and content extraction
* Simplified modular architecture with the following components:
  1. **Core Modules**:
     - `api_doc_crawler.py` - High-level interface that orchestrates the crawling and parsing process
     - `deep_crawler.py` - Implements deep crawling functionality using strategies like `BestFirstCrawlingStrategy`
     - `llm_parser.py` - Implements LLM parsing functionality to filter and extract relevant content
  2. **Configuration Classes**:
     - `CrawlerConfig` - Simple configuration class for crawler parameters
     - `LLMConfig` - Simple configuration class for LLM parameters and instructions
  3. **Utility Functions**:
     - File operations for saving and loading content
* Existing virtual environment (.venv) with all required dependencies