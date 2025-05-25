from crawl4ai.deep_crawling import BestFirstCrawlingStrategy
from crawl4ai.deep_crawling.scorers import KeywordRelevanceScorer
import asyncio
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig
from crawl4ai.content_scraping_strategy import LXMLWebScrapingStrategy

# Create a scorer
scorer = KeywordRelevanceScorer(
    keywords=["crawl", "example", "async", "configuration"],
    weight=0.7
)

# Configure the strategy
strategy = BestFirstCrawlingStrategy(
    max_depth=2,
    include_external=False,
    url_scorer=scorer,
    max_pages=25,              # Maximum number of pages to crawl (optional)
)


async def main():
    # Configure a 2-level deep crawl
    config = CrawlerRunConfig(
        deep_crawl_strategy=strategy,
        scraping_strategy=LXMLWebScrapingStrategy(),
        verbose=True
    )

    async with AsyncWebCrawler() as crawler:
        results = await crawler.arun("https://openai.github.io/openai-agents-python/", config=config)

        print(f"Crawled {len(results)} pages in total")

        # Access individual results
        for result in results[:3]:  # Show first 3 results
            print(f"URL: {result.url}")
            print(f"Depth: {result.metadata.get('depth', 0)}")
            print(f"html: {result.html}")

if __name__ == "__main__":
    asyncio.run(main())