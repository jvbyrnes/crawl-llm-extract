# Decision Log

This file records architectural and implementation decisions using a list format.
2025-05-22 21:15:50 - Initial memory bank creation.

*

## Decision

* Refactor example files into a simplified modular architecture

## Rationale

* Current example files are too large and not modular
* Simplified modular components will improve code reusability and maintainability
* Separation of concerns between crawling and parsing functionality
* Reduced complexity will make the system easier to understand and extend

## Implementation Details

* Will create a simplified modular architecture with the following components:
  1. Core Classes:
     - `ApiDocCrawler` - High-level orchestrator that coordinates crawling and parsing
     - `DeepCrawler` - Implements deep crawling functionality
     - `LLMParser` - Implements LLM parsing functionality
  2. Configuration Classes:
     - `CrawlerConfig` - Simple configuration for crawler parameters
     - `LLMConfig` - Simple configuration for LLM parameters with generic instructions
  3. Utility Functions:
     - Simple file operations for saving and loading content
* Will maintain compatibility with the existing crawl4ai library
* Will ensure the refactored code can be easily imported and used in other projects
* Will focus on simplicity and clarity over complex design patterns

## Updated Decision (2025-05-22 21:44:00)

* Simplified the architecture further by removing factory patterns and complex abstractions
* Focused on essential parameters and functionality in each class
* Created a generic LLM instruction that works for any API documentation type

## Implementation Plan Decision (2025-05-22 21:48:00)

* Created a detailed implementation plan with 8 phases
* Prioritized tasks based on impact and effort
* Established a timeline with dependencies between tasks
* Identified key milestones for tracking progress
* Assessed risks and defined mitigation strategies

## Phase 1 Implementation Decision (2025-05-22 21:55:00)

* Implemented a simplified class structure focusing on core functionality
* Created clear interfaces between components with minimal dependencies
* Used validation in configuration classes to ensure proper usage
* Implemented basic error handling with plans for enhancement in later phases
* Created a command-line interface for easy usage
* Added comprehensive documentation and unit tests
## LLM-Based URL Filtering Implementation (2025-05-25 20:08:00)

* Implemented intelligent post-crawl content filtering using LLM analysis

## Rationale

* User identified that keyword-based filtering was insufficient for precise content targeting
* Example: When crawling Pinecone Python SDK docs, results included irrelevant pages like Rust SDK, Go SDK, etc.
* LLM-based analysis can understand context and semantic relevance much better than simple keyword matching

## Implementation Details

* Created new `URLFilter` class in `src/url_filter.py`:
  - Uses OpenAI API to analyze page content for relevance to target topic
  - Provides relevance scores (0.0-1.0) and explanations
  - Configurable relevance threshold for filtering
  - Handles errors gracefully with fallback scoring

* Updated `ApiDocCrawler` class:
  - Added `target_topic` parameter to constructor
  - Integrated filtering step between crawling and parsing
  - Added `set_target_topic()` method for dynamic updates
  - Enhanced `crawl_and_parse()` and `crawl_only()` methods with filtering
  - Updated result saving to include relevance metadata

* Enhanced command-line interface in `src/main.py`:
  - Added `--target-topic` argument for specifying filtering goal
  - Added `--relevance-threshold` argument for score cutoff
  - Updated help text and examples

* Created comprehensive test script `test_filtering.py`:
  - Demonstrates filtering functionality
  - Shows before/after comparison
  - Tests dynamic topic updates

## Benefits

* **Precision**: Much more accurate content filtering than keyword matching
* **Context-aware**: Understands semantic differences between similar topics
* **Flexible**: Can adapt to any documentation structure or domain
* **Transparent**: Provides explanations for filtering decisions
* **Cost-effective**: Filters before expensive content parsing
## Dual-Model LLM Architecture Implementation (2025-05-25 20:31:00)

* Implemented separate LLM configurations for filtering and extraction tasks

## Rationale

* User requested two different models: one for extraction, one for relevance scoring
* Single model approach was inefficient - using premium models for simple filtering tasks
* Dual-model architecture allows optimization of cost and performance for each task type

## Implementation Details

* **New FilterLLMConfig class** in `src/config.py`:
  - Separate configuration for filtering LLM with required environment variables
  - Validation ensures FILTER_LLM_PROVIDER is set when using filtering
  - Independent temperature and provider settings

* **Updated URLFilter class**:
  - Now uses FilterLLMConfig instead of generic LLMConfig
  - Validates filter configuration on initialization
  - Uses dedicated filtering model for relevance analysis

* **Enhanced ApiDocCrawler**:
  - Added filter_llm_config parameter to constructor
  - Supports dual-model architecture with separate configurations
  - Added set_filter_llm_config() method for dynamic updates

* **Updated command-line interface**:
  - Automatically creates FilterLLMConfig when target_topic is specified
  - Maintains backward compatibility for non-filtering use cases

* **Environment variable requirements**:
  - FILTER_LLM_PROVIDER: Required for filtering functionality
  - FILTER_LLM_TEMPERATURE: Optional, defaults to 0.0 for consistent filtering
  - LLM_PROVIDER: For content extraction (existing)
  - LLM_TEMPERATURE: For content extraction (existing)

## Architecture Benefits

* **Cost Optimization**: Use cheaper models (GPT-3.5-turbo) for filtering, premium models (GPT-4o) for extraction
* **Performance**: Faster relevance scoring with appropriate models
* **Quality**: Better extraction with specialized high-capability models
* **Flexibility**: Independent configuration and scaling of each component
* **Error Handling**: Clear validation and error messages for missing configuration

## Recommended Model Combinations

* **Filtering**: GPT-3.5-turbo, Claude Haiku (fast, cost-effective)
* **Extraction**: GPT-4o, Claude Sonnet (high-quality, comprehensive)