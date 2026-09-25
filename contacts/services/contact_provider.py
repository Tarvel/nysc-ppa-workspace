import os
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict
import httpx
from django.core.cache import cache


@dataclass
class DiscoveredContact:
    """A contact discovered via an external provider."""
    name: str
    role: str = ""
    email: str = ""
    phone: str = ""
    linkedin_url: str = ""
    confidence: str = "Medium"
    verification_status: str = "Provider Sourced"
    source: str = "Hunter.io"

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class HunterContactProvider:
    """Discovers HR contacts via the Hunter.io Domain Search API.

    Free tier: 25 domain searches / month.
    Responses are cached for 24 hours to conserve credits.
    """

    BASE_URL = "https://api.hunter.io/v2/domain-search"

    def __init__(self, api_key: str):
        self.api_key = api_key

    def find_contacts(self, domain: str, department: str = "hr") -> List[DiscoveredContact]:
        """Search Hunter.io for contacts at *domain* in the given department."""
        if not domain:
            return []

        # Check cache first (24h TTL)
        cache_key = f"hunter_contacts_{domain}_{department}"
        cached = cache.get(cache_key)
        if cached is not None:
            print(f"Hunter.io cache hit for {domain}")
            return [DiscoveredContact(**c) for c in cached]

        params = {
            "domain": domain,
            "department": department,
            "api_key": self.api_key,
        }

        try:
            with httpx.Client(timeout=15.0) as client:
                resp = client.get(self.BASE_URL, params=params)
                resp.raise_for_status()
                data = resp.json()

            contacts = self._parse_response(data, domain)

            # Cache for 24 hours
            cache.set(cache_key, [c.to_dict() for c in contacts], 86400)

            print(f"Hunter.io found {len(contacts)} HR contact(s) for {domain}")
            return contacts

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 429:
                print(f"Hunter.io rate limit reached for {domain}")
            elif e.response.status_code == 401:
                print("Hunter.io API key is invalid")
            else:
                print(f"Hunter.io HTTP error for {domain}: {e}")
            return []
        except Exception as e:
            print(f"Hunter.io error for {domain}: {e}")
            return []

    def _parse_response(self, data: Dict[str, Any], domain: str) -> List[DiscoveredContact]:
        """Parse the Hunter.io domain-search response into DiscoveredContact objects."""
        contacts: List[DiscoveredContact] = []
        emails_data = data.get("data", {}).get("emails", [])

        for item in emails_data:
            first = item.get("first_name", "") or ""
            last = item.get("last_name", "") or ""
            name = f"{first} {last}".strip() or "HR Contact"

            email = item.get("value", "")
            position = item.get("position", "") or ""
            linkedin = item.get("linkedin", "") or ""
            phone_number = item.get("phone_number", "") or ""

            # Map Hunter confidence (0-100) to our High/Medium/Low
            hunter_confidence = item.get("confidence", 0) or 0
            if hunter_confidence >= 80:
                confidence = "High"
            elif hunter_confidence >= 50:
                confidence = "Medium"
            else:
                confidence = "Low"

            contacts.append(DiscoveredContact(
                name=name,
                role=position or "HR Department",
                email=email,
                phone=phone_number,
                linkedin_url=linkedin,
                confidence=confidence,
                verification_status="Provider Sourced",
                source="Hunter.io",
            ))

        return contacts


class MockContactProvider:
    """Returns realistic mock HR contacts when no API key is configured."""

    def find_contacts(self, domain: str, department: str = "hr") -> List[DiscoveredContact]:
        if not domain:
            return []

        company = domain.split(".")[0].title()
        return [
            DiscoveredContact(
                name=f"{company} HR Desk",
                role="Talent Acquisition / HR",
                email=f"hr@{domain}",
                confidence="Medium",
                verification_status="Provider Sourced",
                source="Mock Provider (set HUNTER_API_KEY for real lookups)",
            ),
            DiscoveredContact(
                name=f"{company} Careers",
                role="Recruitment",
                email=f"careers@{domain}",
                confidence="Low",
                verification_status="Provider Sourced",
                source="Mock Provider (set HUNTER_API_KEY for real lookups)",
            ),
        ]


def get_contact_provider():
    """Factory: returns HunterContactProvider if HUNTER_API_KEY is set, else MockContactProvider."""
    key = os.getenv("HUNTER_API_KEY")
    if key:
        return HunterContactProvider(key)
    return MockContactProvider()


def extract_domain(url: str) -> str:
    """Extract a clean domain from a URL.

    >>> extract_domain("https://www.paystack.com/about")
    'paystack.com'
    >>> extract_domain("http://google.com")
    'google.com'
    """
    if not url:
        return ""
    try:
        from urllib.parse import urlparse
        parsed = urlparse(url if "://" in url else f"https://{url}")
        host = parsed.hostname or ""
        # Strip 'www.' prefix
        if host.startswith("www."):
            host = host[4:]
        return host
    except Exception:
        return ""
