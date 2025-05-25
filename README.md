# API Documentation Crawler

A tool for crawling and parsing online programming API documentation.

## Overview

This project provides a modular system for crawling and parsing online programming API documentation. It uses web crawling techniques to navigate through documentation pages and leverages Large Language Models (LLMs) to extract and format the relevant content.

## Features

- Deep crawling of API documentation websites
- LLM-based content parsing and filtering
- Keyword-based relevance scoring for crawling
- Configurable crawling depth and scope
- Output in clean markdown format

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
   Then edit the `.env` file to add your OpenAI API key and customize other settings.

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
  --include-external
```

### Options

- `url`: URL of the API documentation (required)
- `--output-dir`: Directory to save the results (default: "output")
- `--keywords`: Comma-separated list of keywords for relevance scoring
- `--max-depth`: Maximum depth for crawling (default: 2)
- `--max-pages`: Maximum number of pages to crawl (default: 25)
- `--include-external`: Include external links (default: false)

## Project Structure

```
api-doc-crawler/
├── src/                  # Source code
│   ├── __init__.py       # Package initialization
│   ├── config.py         # Configuration classes
│   ├── deep_crawler.py   # Deep crawling functionality
│   ├── llm_parser.py     # LLM parsing functionality
│   ├── api_doc_crawler.py # High-level orchestrator
│   └── main.py           # Command-line interface
├── tests/                # Test files
├── config/               # Configuration files
└── output/               # Output directory for results
```

## Running Tests

```bash
python -m unittest discover tests
```

## Example

Crawling the Python requests library documentation:

```bash
python -m src.main https://requests.readthedocs.io/en/latest/ \
  --keywords http,request,response,api,method \
  --max-depth 2
```

## License

MIT

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.