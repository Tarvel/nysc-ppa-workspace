import os
from typing import Protocol, List, Dict, Any
import httpx
from django.core.cache import cache

class SearchResult:
    def __init__(self, title: str, url: str, snippet: str, domain: str = "", is_mock: bool = False):
        self.title = title
        self.url = url
        self.snippet = snippet
        self.domain = domain
        self.is_mock = is_mock

    def to_dict(self):
        return {
            'title': self.title,
            'url': self.url,
            'snippet': self.snippet,
            'domain': self.domain,
            'is_mock': self.is_mock
        }

class SearchProvider(Protocol):
    def search(self, query: str, num_results: int = 3) -> List[SearchResult]:
        ...

class TavilySearchProvider:
    def __init__(self, api_key: str):
        self.api_key = api_key

    def search(self, query: str, num_results: int = 3) -> List[SearchResult]:
        cache_key = f"tavily_search_{hash(query)}_{num_results}"
        cached = cache.get(cache_key)
        if cached:
            return [SearchResult(**item) for item in cached]

        url = "https://api.tavily.com/search"
        payload = {
            "api_key": self.api_key,
            "query": query,
            "max_results": num_results
        }
        try:
            with httpx.Client(timeout=10.0) as client:
                resp = client.post(url, json=payload)
                resp.raise_for_status()
                data = resp.json()
                results = []
                for item in data.get("results", []):
                    res = SearchResult(
                        title=item.get("title", ""),
                        url=item.get("url", ""),
                        snippet=item.get("content", ""),
                        domain=item.get("url", "").split('/')[2] if '://' in item.get("url", "") else ""
                    )
                    results.append(res)
                
                # Cache search results for 24 hours to conserve API credits
                cache.set(cache_key, [r.to_dict() for r in results], 86400)
                return results
        except Exception as e:
            print(f"Tavily Search Error: {e}")
            return MockSearchProvider().search(query, num_results)

class MockSearchProvider:
    """Fallback provider when no search API keys are configured."""
    def search(self, query: str, num_results: int = 3) -> List[SearchResult]:
        company = query.split()[0] if query else "Company"
        results = [
            SearchResult(
                title=f"[DEMO DATA] {company} Official Website & Overview",
                url=f"https://www.{company.lower().replace(' ', '')}.com",
                snippet=f"{company} is a leading organization in Nigeria providing technology, financial, or industrial services. Headquartered in Abuja.",
                domain=f"{company.lower()}.com",
                is_mock=True
            ),
            SearchResult(
                title=f"[DEMO DATA] {company} Careers & Graduate Opportunities",
                url=f"https://www.{company.lower().replace(' ', '')}.com/careers",
                snippet=f"Explore careers, internship placements, and NYSC Corps Member postings at {company}. We hire IT support, software engineers, and analysts.",
                domain=f"{company.lower()}.com",
                is_mock=True
            ),
            SearchResult(
                title=f"[DEMO DATA] {company} LinkedIn Company Page",
                url=f"https://www.linkedin.com/company/{company.lower()}",
                snippet=f"Official LinkedIn profile for {company}. Check employees, HR acquisition leads, and alumni.",
                domain="linkedin.com",
                is_mock=True
            )
        ]
        return results[:num_results]

def get_search_provider() -> SearchProvider:
    tavily_key = os.getenv("TAVILY_API_KEY")
    if tavily_key:
        return TavilySearchProvider(tavily_key)
    return MockSearchProvider()
