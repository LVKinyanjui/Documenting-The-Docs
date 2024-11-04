from collections import namedtuple
import aiohttp
import asyncio
from typing import List, NamedTuple
import time

class FetchResult(NamedTuple):
    url: str
    response: str
    time_taken: float
    status_code: int
    success: bool
    error_message: str | None

async def fetch_url(session: aiohttp.ClientSession, url: str) -> FetchResult:
    """
    Fetch a single URL and return a FetchResult named tuple.
    """
    start_time = time.time()
    try:
        async with session.get(url) as response:
            text = await response.text()
            return FetchResult(
                url=url,
                response=text,
                time_taken=time.time() - start_time,
                status_code=response.status,
                success=response.status < 400,
                error_message=None
            )
    except Exception as e:
        return FetchResult(
            url=url,
            response="",
            time_taken=time.time() - start_time,
            status_code=0,
            success=False,
            error_message=str(e)
        )

async def fetch_all_urls(urls: List[str], max_concurrent: int = 5) -> List[FetchResult]:
    """
    Fetch multiple URLs concurrently with a limit on concurrent requests.
    
    Args:
        urls: List of URLs to fetch
        max_concurrent: Maximum number of concurrent requests
    
    Returns:
        List of FetchResult named tuples
    """
    connector = aiohttp.TCPConnector(limit=max_concurrent)
    async with aiohttp.ClientSession(connector=connector) as session:
        tasks = [fetch_url(session, url) for url in urls]
        results = await asyncio.gather(*tasks)
        return results

def main(urls: List[str], max_concurrent: int = 5):
    """
    Main function to run the async requests.
    
    Args:
        urls: List of URLs to fetch
        max_concurrent: Maximum number of concurrent requests
    """
    start_time = time.time()
    results = asyncio.run(fetch_all_urls(urls, max_concurrent))
    
    print(f"\nResults for {len(urls)} URLs:")
    print("-" * 50)
    for result in results:
        print(f"URL: {result.url}")
        if result.success:
            print(f"Status Code: {result.status_code}")
            print(f"Response length: {len(result.response)} characters")
        else:
            print(f"Error: {result.error_message}")
        print(f"Time taken: {result.time_taken:.2f} seconds")
        print("-" * 50)
    
    # Summary statistics
    successful_requests = sum(1 for r in results if r.success)
    print(f"\nSummary:")
    print(f"Total requests: {len(results)}")
    print(f"Successful requests: {successful_requests}")
    print(f"Failed requests: {len(results) - successful_requests}")
    print(f"Total time taken: {time.time() - start_time:.2f} seconds")

if __name__ == "__main__":
    # Example usage
    urls_to_fetch = [
        "https://api.example.com/endpoint1",
        "https://api.example.com/endpoint2",
        "https://api.example.com/endpoint3",
    ]
    
    main(urls_to_fetch, max_concurrent=5)

# Example of how to use the results in your own code:
"""
results = asyncio.run(fetch_all_urls(urls_to_fetch, max_concurrent=5))
for result in results:
    if result.success:
        print(f"Successfully fetched {result.url} with status {result.status_code}")
        print(f"Response content: {result.response[:100]}...")  # First 100 chars
    else:
        print(f"Failed to fetch {result.url}: {result.error_message}")
    print(f"Request took {result.time_taken:.2f} seconds")
"""