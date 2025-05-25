# System Patterns *Optional*

This file documents recurring patterns and standards used in the project.
It is optional, but recommended to be updated as the project evolves.
2025-05-22 21:16:00 - Initial memory bank creation.

*

## Coding Patterns

* Async/await pattern for web crawling operations
* Strategy pattern for different crawling and scraping approaches
* Simple class-based configuration
* Direct composition over dependency injection

## Architectural Patterns

* Simplified modular design with clear separation of concerns
* High-level orchestrator (`ApiDocCrawler`) coordinating specialized components
* Configuration-based approach using simple parameter classes
* Pipeline architecture for processing crawled content
* Minimalist design focusing on essential functionality

## Testing Patterns

* Unit testing for individual classes with mock dependencies
* Integration testing for class interactions
* Example-based testing for demonstrating functionality
* Simplified test cases focusing on core functionality

## Updated Patterns (2025-05-22 21:45:00)

* Removed complex factory patterns in favor of simple configuration classes
* Focused on direct composition of objects rather than complex dependency injection
* Simplified interfaces between components
* Adopted a more pragmatic approach to architecture