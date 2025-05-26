# API Documentation Crawler - Detailed Technical Architecture
*Generated: 2025-05-25*

## Detailed Class and Component Diagram

```mermaid
classDiagram
    %% Configuration Classes
    class CrawlerConfig {
        +int max_depth
        +bool include_external
        +int max_pages
        +list keywords
        +float keyword_weight
        +__init__(max_depth, include_external, max_pages)
        +_get_env_int(key, default) int
        +_get_env_bool(key, default) bool
        +_get_env_float(key, default) float
        +set_keywords(keywords, weight)
        +validate()
        +__str__() str
    }
    
    class LLMConfig {
        +str provider
        +float temperature
        +str instruction
        +__init__(provider, temperature)
        +_get_env_float(key, default) float
        +get_generic_instruction() str
        +set_custom_instruction(instruction)
        +validate()
        +__str__() str
    }
    
    class FilterLLMConfig {
        +str provider
        +float temperature
        +__init__(provider, temperature)
        +_get_env_float(key, default) float
        +validate()
        +__str__() str
    }
    
    %% Core Classes
    class ApiDocCrawler {
        +CrawlerConfig crawler_config
        +LLMConfig llm_config
        +FilterLLMConfig filter_llm_config
        +str target_topic
        +bool filtering_enabled
        +DeepCrawler crawler
        +URLFilter url_filter
        +LLMParser parser
        +__init__(crawler_config, llm_config, filter_llm_config, target_topic, filtering_enabled)
        +crawl_and_parse(url) List~Dict~
        +crawl_only(url) List~Dict~
        +parse_only(html_content) List~str~
        +set_target_topic(target_topic)
        +set_filter_llm_config(filter_llm_config)
        +save_results(results, output_dir)
    }
    
    class DeepCrawler {
        +CrawlerConfig config
        +AsyncWebCrawler crawler
        +__init__(config)
        +crawl(url) List~Dict~
        +_process_result(result) Dict
    }
    
    class URLFilter {
        +FilterLLMConfig filter_llm_config
        +str target_topic
        +__init__(filter_llm_config, target_topic)
        +filter_crawled_results(crawled_results) List~Dict~
        +_analyze_page_inclusion(page_result) Tuple~bool, str~
        +_create_inclusion_prompt(url, title, content_sample) str
        +_parse_inclusion_response(response_text) Tuple~bool, str~
        +set_target_topic(target_topic)
    }
    
    class LLMParser {
        +LLMConfig config
        +dict usage_stats
        +__init__(config)
        +parse(html_content) List~str~
        +show_usage() Dict
    }
    
    %% External Dependencies
    class AsyncWebCrawler {
        <<external>>
        +arun(url, config) CrawlResult
    }
    
    class OpenAI_Client {
        <<external>>
        +chat.completions.create() ChatCompletion
    }
    
    %% Relationships
    ApiDocCrawler --> CrawlerConfig : uses
    ApiDocCrawler --> LLMConfig : uses
    ApiDocCrawler --> FilterLLMConfig : uses
    ApiDocCrawler --> DeepCrawler : orchestrates
    ApiDocCrawler --> URLFilter : orchestrates
    ApiDocCrawler --> LLMParser : orchestrates
    
    DeepCrawler --> CrawlerConfig : configured by
    DeepCrawler --> AsyncWebCrawler : uses
    
    URLFilter --> FilterLLMConfig : configured by
    URLFilter --> OpenAI_Client : uses (filtering)
    
    LLMParser --> LLMConfig : configured by
    LLMParser --> OpenAI_Client : uses (extraction)
    
    %% Environment Variables
    class Environment {
        <<interface>>
        LLM_PROVIDER
        LLM_TEMPERATURE
        FILTER_LLM_PROVIDER
        FILTER_LLM_TEMPERATURE
        OPENAI_API_KEY
        MAX_DEPTH
        MAX_PAGES
        INCLUDE_EXTERNAL
    }
    
    CrawlerConfig ..> Environment : reads
    LLMConfig ..> Environment : reads
    FilterLLMConfig ..> Environment : reads
```

## Detailed Process Flow Diagram

```mermaid
sequenceDiagram
    participant CLI as Command Line
    participant AC as ApiDocCrawler
    participant DC as DeepCrawler
    participant UF as URLFilter
    participant LP as LLMParser
    participant C4AI as crawl4ai
    participant FLLM as Filter LLM
    participant ELLM as Extraction LLM
    participant FS as File System
    
    %% Initialization Phase
    CLI->>AC: Initialize with configs + filtering_enabled
    AC->>DC: Create DeepCrawler
    alt filtering_enabled AND target_topic
        AC->>UF: Create URLFilter
    else
        AC->>AC: url_filter = None
    end
    AC->>LP: Create LLMParser
    
    %% Crawling Phase
    CLI->>AC: crawl_and_parse(url)
    AC->>DC: crawl(url)
    DC->>C4AI: arun(url, strategy)
    C4AI-->>DC: CrawlResult[]
    DC-->>AC: processed_results[]
    
    %% Binary Filtering Phase (opt-in only)
    alt filtering_enabled AND target_topic AND url_filter exists
        AC->>UF: filter_crawled_results(results)
        loop for each page
            UF->>FLLM: analyze_page_inclusion(page)
            FLLM-->>UF: {decision: "include/exclude", explanation}
            UF->>UF: parse_inclusion_response()
        end
        UF-->>AC: filtered_results[]
    else
        AC->>AC: Keep all crawled pages (no filtering)
    end
    
    %% Content Extraction Phase
    loop for each filtered page
        AC->>LP: parse(html_content)
        LP->>ELLM: chat.completions.create()
        ELLM-->>LP: extracted_content
        LP-->>AC: parsed_sections[]
    end
    
    %% Output Phase
    AC->>FS: save_results(results, output_dir)
    AC->>FS: create index.html
    AC-->>CLI: completion_status
```

## LLM Integration Details

```mermaid
flowchart TD
    subgraph "Dual-Model LLM Architecture"
        subgraph "Filter Model (Fast & Cheap)"
            FM[Filter LLM<br/>gpt-3.5-turbo / o1-mini]
            FP[Binary Decision Prompt<br/>Include/Exclude + Explanation]
            FR[JSON Response<br/>{decision, explanation}]
        end
        
        subgraph "Extraction Model (Premium)"
            EM[Extraction LLM<br/>gpt-4o / o1-preview]
            EP[Content Extraction Prompt<br/>Generic API Documentation]
            ER[Structured Content<br/>Markdown Sections]
        end
    end
    
    subgraph "Model Compatibility"
        O1[o1 Model Detection<br/>No system messages<br/>No temperature/max_tokens]
        STD[Standard Models<br/>System + User messages<br/>Full parameter support]
    end
    
    %% Flow
    URLFilter --> FM
    FM --> FP
    FP --> FR
    
    LLMParser --> EM
    EM --> EP
    EP --> ER
    
    FM -.-> O1
    EM -.-> O1
    FM -.-> STD
    EM -.-> STD
```

## Configuration and Environment Flow

```mermaid
flowchart LR
    subgraph "Environment Variables"
        ENV1[LLM_PROVIDER<br/>LLM_TEMPERATURE]
        ENV2[FILTER_LLM_PROVIDER<br/>FILTER_LLM_TEMPERATURE]
        ENV3[MAX_DEPTH<br/>MAX_PAGES<br/>INCLUDE_EXTERNAL]
        ENV4[OPENAI_API_KEY]
    end
    
    subgraph "Configuration Classes"
        LC[LLMConfig<br/>Extraction Model]
        FC[FilterLLMConfig<br/>Filter Model]
        CC[CrawlerConfig<br/>Crawl Parameters]
    end
    
    subgraph "Validation & Defaults"
        VAL[validate()<br/>Environment checks<br/>Default values<br/>Error handling]
    end
    
    ENV1 --> LC
    ENV2 --> FC
    ENV3 --> CC
    ENV4 --> LC
    ENV4 --> FC
    
    LC --> VAL
    FC --> VAL
    CC --> VAL
    
    VAL --> ApiDocCrawler
```

## Error Handling and Fallbacks

```mermaid
flowchart TD
    subgraph "Error Handling Strategy"
        CE[Configuration Errors<br/>Missing env vars<br/>Invalid values]
        NE[Network Errors<br/>Crawling failures<br/>Timeout handling]
        LE[LLM Errors<br/>API failures<br/>Response parsing]
        FE[File System Errors<br/>Permission issues<br/>Disk space]
    end
    
    subgraph "Fallback Mechanisms"
        CF[Config Fallbacks<br/>Default values<br/>Environment detection]
        NF[Network Fallbacks<br/>Retry logic<br/>Graceful degradation]
        LF[LLM Fallbacks<br/>Default decisions<br/>Error responses]
        FF[File Fallbacks<br/>Alternative paths<br/>Error logging]
    end
    
    CE --> CF
    NE --> NF
    LE --> LF
    FE --> FF
```

## Key Technical Features

### Filtering Opt-In Enhancement (2025-05-26)
- **Explicit Control**: Filtering now requires both `--enable-filtering` flag and `--target-topic`
- **Performance Optimization**: No LLM calls when filtering disabled (default behavior)
- **Cost Management**: Filter LLM API usage only when explicitly requested
- **Clear Intent**: Users must explicitly opt-in to filtering behavior

### Binary Filtering Enhancement (2025-05-25)
- **Simplified Decision Making**: Replaced 0.0-1.0 scoring with include/exclude
- **Eliminated Thresholds**: No more arbitrary cutoff configuration
- **Maintained Transparency**: Decision explanations preserved
- **Improved UX**: More intuitive binary decisions

### Dual-Model Architecture Benefits
- **Cost Optimization**: Cheap models for filtering, premium for extraction
- **Performance**: Fast relevance decisions with appropriate models
- **Quality**: High-quality extraction with capable models
- **Flexibility**: Independent scaling and configuration

### Async Processing Patterns
- **Concurrent Crawling**: Multiple pages processed simultaneously
- **Non-blocking LLM Calls**: Async API interactions
- **Resource Management**: Proper cleanup and connection handling