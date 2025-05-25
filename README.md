# API Documentation Crawler

A tool for crawling and parsing online programming API documentation.

## Overview

This project provides a modular system for crawling and parsing online programming API documentation. It uses web crawling techniques to navigate through documentation pages and leverages Large Language Models (LLMs) to extract and format the relevant content.

## Features

- Deep crawling of API documentation websites
- **NEW: Dual-Model LLM Architecture** - Separate optimized models for filtering and extraction
- **NEW: LLM-based intelligent URL filtering** - Filter crawled pages by relevance to specific topics
- LLM-based content parsing and filtering
- Keyword-based relevance scoring for crawling
- Configurable crawling depth and scope
- Output in clean markdown format with relevance scores

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/api-doc-crawler.git
   cd api-doc-crawler
   ```

2. Create a virtual environment and install dependencies:
   ```
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. Set up your environment variables:
   ```
   cp .env.example .env
   ```
   Then edit the `.env` file to add your OpenAI API key and configure the dual-model setup:
   
   **Required for filtering functionality:**
   ```bash
   # Content extraction model (premium model for quality)
   LLM_PROVIDER=openai/gpt-4o
   LLM_TEMPERATURE=0.1
   
   # Relevance filtering model (fast/cheap model for efficiency)
   FILTER_LLM_PROVIDER=openai/gpt-3.5-turbo
   FILTER_LLM_TEMPERATURE=0.0
   ```

## Usage

### Basic Usage

```bash
python -m src.main https://docs.example.com/api
```

### Advanced Options

```bash
python -m src.main https://docs.example.com/api \
  --output-dir custom_output \
  --keywords api,function,method,parameter \
  --max-depth 3 \
  --max-pages 50 \
  --include-external \
  --target-topic "Python SDK documentation" \
  --relevance-threshold 0.8
```

### Dual-Model LLM Architecture (NEW!)

The system now uses **two separate LLM models** for optimal performance:

- **Filtering Model** (`FILTER_LLM_PROVIDER`): Fast, cost-effective model for relevance scoring
- **Extraction Model** (`LLM_PROVIDER`): High-quality model for content extraction

```bash
# Focus on Python SDK documentation only with dual-model setup
python -m src.main https://docs.pinecone.io/reference/python-sdk \
  --target-topic "Python SDK documentation for Pinecone vector database" \
  --relevance-threshold 0.7
```

**How it works:**
1. **Crawl** all available pages
2. **Filter** using fast model (GPT-3.5-turbo) to analyze relevance
3. **Extract** using premium model (GPT-4o) for high-quality content parsing
4. **Save** only the most relevant, well-extracted content

**Benefits:**
- **Cost-effective**: Use cheaper models for filtering, premium for extraction
- **Fast**: Quick relevance decisions with optimized filtering model
- **High-quality**: Best extraction results with capable models

### Options

- `url`: URL of the API documentation (required)
- `--output-dir`: Directory to save the results (default: "output")
- `--keywords`: Comma-separated list of keywords for relevance scoring
- `--max-depth`: Maximum depth for crawling (default: 2)
- `--max-pages`: Maximum number of pages to crawl (default: 25)
- `--include-external`: Include external links (default: false)
- `--target-topic`: **NEW!** Target topic for LLM-based filtering (e.g., "Python SDK documentation")
- `--relevance-threshold`: **NEW!** Minimum relevance score (0.0-1.0) to include page (default: 0.7)

## Project Structure

```
api-doc-crawler/
├── src/                  # Source code
│   ├── __init__.py       # Package initialization
│   ├── config.py         # Configuration classes
│   ├── deep_crawler.py   # Deep crawling functionality
│   ├── llm_parser.py     # LLM parsing functionality
│   ├── url_filter.py     # NEW! LLM-based URL filtering
│   ├── api_doc_crawler.py # High-level orchestrator
│   └── main.py           # Command-line interface
├── tests/                # Test files
├── config/               # Configuration files
├── test_filtering.py     # NEW! Test script for filtering functionality
└── output/               # Output directory for results
```

## Running Tests

```bash
python -m unittest discover tests
```

## Examples

### Basic Crawling
Crawling the Python requests library documentation:

```bash
python -m src.main https://requests.readthedocs.io/en/latest/ \
  --keywords http,request,response,api,method \
  --max-depth 2
```

### Smart Filtering Example
Crawling Pinecone documentation but only keeping Python SDK pages:

```bash
python -m src.main https://docs.pinecone.io/reference/python-sdk \
  --target-topic "Python SDK documentation for Pinecone vector database" \
  --relevance-threshold 0.7 \
  --output-dir pinecone_python_sdk
```

This will automatically filter out pages about other SDKs (Rust, Go, Java, etc.) and focus only on Python-specific content.

### Testing the New Filtering Feature

Run the test script to see the filtering in action:

```bash
python test_filtering.py
```

This will demonstrate how the LLM evaluates page relevance and filters results.

## License

MIT

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.