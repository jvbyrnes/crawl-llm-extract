# Filtering Opt-In Decision Flow
*Generated: 2025-05-26*

## Command-Line Filtering Decision Flow

```mermaid
flowchart TD
    START[User runs crawler command] --> CHECK_FLAGS{Check command-line flags}
    
    CHECK_FLAGS --> NO_FLAGS[No filtering flags<br/>--url only]
    CHECK_FLAGS --> ENABLE_ONLY[--enable-filtering only<br/>No --target-topic]
    CHECK_FLAGS --> TARGET_ONLY[--target-topic only<br/>No --enable-filtering]
    CHECK_FLAGS --> BOTH_FLAGS[Both flags provided<br/>--enable-filtering + --target-topic]
    
    NO_FLAGS --> DEFAULT[✅ Default Behavior<br/>No filtering applied<br/>Keep all crawled pages]
    
    ENABLE_ONLY --> ERROR[❌ Error<br/>--target-topic is required<br/>when --enable-filtering is used]
    
    TARGET_ONLY --> NO_FILTER[✅ No Filtering<br/>Target topic ignored<br/>Keep all crawled pages]
    
    BOTH_FLAGS --> VALIDATE{Validate FilterLLMConfig}
    
    VALIDATE -->|Valid| FILTERING[✅ LLM Filtering Enabled<br/>Binary include/exclude decisions<br/>Filter LLM API calls]
    VALIDATE -->|Invalid| CONFIG_ERROR[❌ Configuration Error<br/>Missing FILTER_LLM_PROVIDER<br/>or OPENAI_API_KEY]
    
    DEFAULT --> CRAWL_ALL[Crawl → Keep All → Parse All]
    NO_FILTER --> CRAWL_ALL
    FILTERING --> CRAWL_FILTER[Crawl → Filter → Parse Filtered]
    
    ERROR --> EXIT[Exit with error code 2]
    CONFIG_ERROR --> EXIT
    
    CRAWL_ALL --> SUCCESS[✅ Success<br/>All pages processed]
    CRAWL_FILTER --> SUCCESS
    
    %% Styling
    classDef success fill:#e8f5e8,stroke:#1b5e20,stroke-width:2px
    classDef error fill:#ffebee,stroke:#c62828,stroke-width:2px
    classDef process fill:#e3f2fd,stroke:#1565c0,stroke-width:2px
    classDef decision fill:#fff3e0,stroke:#ef6c00,stroke-width:2px
    
    class DEFAULT,NO_FILTER,FILTERING,SUCCESS success
    class ERROR,CONFIG_ERROR,EXIT error
    class CRAWL_ALL,CRAWL_FILTER process
    class CHECK_FLAGS,VALIDATE decision
```

## ApiDocCrawler Initialization Flow

```mermaid
flowchart TD
    INIT[ApiDocCrawler.__init__] --> CHECK_PARAMS{Check parameters}
    
    CHECK_PARAMS --> FILTERING_DISABLED[filtering_enabled = False]
    CHECK_PARAMS --> FILTERING_ENABLED[filtering_enabled = True]
    
    FILTERING_DISABLED --> NO_FILTER_CONFIG[filter_llm_config ignored<br/>url_filter = None]
    
    FILTERING_ENABLED --> CHECK_CONFIG{filter_llm_config provided?}
    
    CHECK_CONFIG -->|Yes| VALIDATE_CONFIG[Validate FilterLLMConfig]
    CHECK_CONFIG -->|No| USE_DEFAULT[Use default FilterLLMConfig]
    
    VALIDATE_CONFIG --> CREATE_FILTER[Create URLFilter instance]
    USE_DEFAULT --> CREATE_FILTER
    
    NO_FILTER_CONFIG --> READY_NO_FILTER[✅ Ready - No Filtering]
    CREATE_FILTER --> READY_WITH_FILTER[✅ Ready - With Filtering]
    
    %% Styling
    classDef ready fill:#e8f5e8,stroke:#1b5e20,stroke-width:2px
    classDef process fill:#e3f2fd,stroke:#1565c0,stroke-width:2px
    classDef decision fill:#fff3e0,stroke:#ef6c00,stroke-width:2px
    
    class READY_NO_FILTER,READY_WITH_FILTER ready
    class NO_FILTER_CONFIG,VALIDATE_CONFIG,USE_DEFAULT,CREATE_FILTER process
    class CHECK_PARAMS,CHECK_CONFIG decision
```

## Filtering Logic During Crawl

```mermaid
flowchart TD
    CRAWL_COMPLETE[Crawling completed<br/>Found N pages] --> CHECK_FILTER{filtering_enabled?}
    
    CHECK_FILTER -->|False| SKIP_FILTER[Skip filtering<br/>Log: "Filtering disabled - keeping all crawled pages"]
    CHECK_FILTER -->|True| CHECK_COMPONENTS{url_filter exists?<br/>target_topic set?}
    
    CHECK_COMPONENTS -->|No| SKIP_FILTER
    CHECK_COMPONENTS -->|Yes| APPLY_FILTER[Apply LLM filtering<br/>Log: "Filtering for inclusion based on: {topic}"]
    
    SKIP_FILTER --> ALL_PAGES[Keep all N pages<br/>No LLM API calls]
    
    APPLY_FILTER --> FILTER_LOOP[For each page:<br/>LLM binary decision<br/>Include/Exclude + Explanation]
    
    FILTER_LOOP --> FILTERED_PAGES[Keep M pages (M ≤ N)<br/>Log: "Filtered results: M/N pages kept"]
    
    ALL_PAGES --> PARSE_ALL[Parse all N pages]
    FILTERED_PAGES --> PARSE_FILTERED[Parse M filtered pages]
    
    PARSE_ALL --> RESULT_NO_FILTER[Results with no filtering metadata<br/>Log: "No filtering applied - all crawled pages were kept"]
    PARSE_FILTERED --> RESULT_WITH_FILTER[Results with filtering metadata<br/>included: true/false<br/>decision_explanation: "..."]
    
    %% Styling
    classDef nofilter fill:#e8f5e8,stroke:#1b5e20,stroke-width:2px
    classDef filtered fill:#e3f2fd,stroke:#1565c0,stroke-width:2px
    classDef decision fill:#fff3e0,stroke:#ef6c00,stroke-width:2px
    classDef process fill:#f3e5f5,stroke:#4a148c,stroke-width:2px
    
    class SKIP_FILTER,ALL_PAGES,PARSE_ALL,RESULT_NO_FILTER nofilter
    class APPLY_FILTER,FILTER_LOOP,FILTERED_PAGES,PARSE_FILTERED,RESULT_WITH_FILTER filtered
    class CHECK_FILTER,CHECK_COMPONENTS decision
    class CRAWL_COMPLETE process
```

## Key Benefits of Opt-In Design

### Performance Benefits
- **Default Fast Path**: No LLM filtering calls when not explicitly requested
- **Reduced Latency**: Faster crawling for users who want everything
- **Resource Efficiency**: No unnecessary API calls or processing

### Cost Benefits
- **Predictable Costs**: Filter LLM usage only when explicitly enabled
- **User Control**: Clear opt-in prevents surprise API charges
- **Budget Management**: Users can choose when to incur filtering costs

### User Experience Benefits
- **Explicit Intent**: Clear command-line flags show filtering intention
- **Error Prevention**: Validation prevents incomplete flag combinations
- **Backward Compatibility**: Existing usage patterns continue to work

### Technical Benefits
- **Clean Architecture**: Conditional initialization based on explicit flags
- **Maintainability**: Clear separation between filtered and non-filtered paths
- **Testability**: Easy to test both filtering enabled and disabled scenarios

## Migration Guide

### Before (Automatic Filtering)
```bash
# This would automatically enable filtering
python -m src.main https://docs.example.com --target-topic "Python SDK"
```

### After (Explicit Opt-In)
```bash
# This now keeps all pages (no filtering)
python -m src.main https://docs.example.com --target-topic "Python SDK"

# This enables filtering (explicit opt-in)
python -m src.main https://docs.example.com --enable-filtering --target-topic "Python SDK"
```

### Breaking Change Notice
Users who previously relied on automatic filtering when `--target-topic` was provided will need to add the `--enable-filtering` flag to maintain the same behavior.