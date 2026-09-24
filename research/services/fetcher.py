import httpx
from bs4 import BeautifulSoup
import re
from urllib.parse import urlparse

class WebPageFetcher:
    """Safely fetches and parses web content for research ingestion."""
    
    @staticmethod
    def fetch(url: str, timeout: float = 10.0) -> dict:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        try:
            with httpx.Client(follow_redirects=True, timeout=timeout, headers=headers) as client:
                response = client.get(url)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Remove script, style, nav, footer tags for clean content extraction
                for tag in soup(['script', 'style', 'noscript', 'svg', 'header', 'footer']):
                    tag.decompose()
                
                title = soup.title.string.strip() if soup.title and soup.title.string else urlparse(url).netloc
                
                # Extract clean readable text
                text_content = soup.get_text(separator=' ', strip=True)
                # Clean up excess spaces
                clean_text = re.sub(r'\s+', ' ', text_content)[:4000] # Limit to 4k chars snippet
                
                domain = urlparse(url).netloc
                
                return {
                    'success': True,
                    'url': url,
                    'domain': domain,
                    'title': title[:250],
                    'excerpt': clean_text,
                    'error': None
                }
        except Exception as e:
            return {
                'success': False,
                'url': url,
                'domain': urlparse(url).netloc,
                'title': url,
                'excerpt': '',
                'error': str(e)
            }
