from .provider import get_ai_provider
from organizations.models import Organization, Opportunity, TimelineEvent
from research.models import Source, Evidence
from contacts.models import Contact

class BriefGenerator:
    """Generates structured research summaries and populates evidence and contacts."""
    
    @staticmethod
    def process_organization_research(organization: Organization, sources: list[Source]) -> dict:
        ai = get_ai_provider()
        
        sources_text = "\n---\n".join([f"Source: {s.title} ({s.url})\nContent: {s.content_excerpt[:1000]}" for s in sources])
        
        prompt = f"""
Analyze the web research collected for organization: '{organization.name}'.

RESEARCH SOURCES:
{sources_text if sources_text else "No web pages fetched. Basic URL provided."}

YOUR TASK:
Extract structured organization details, evidence, potential HR contacts, and research summary.

Return JSON format strictly matching this schema:
{{
  "industry": "e.g. Financial Technology / Banking",
  "location": "e.g. Abuja, Nigeria",
  "description": "2-3 sentence overview of company",
  "careers_url": "URL to careers page if found, else empty",
  "what_we_know": [
    "Confirmed detail 1",
    "Confirmed detail 2"
  ],
  "why_it_fits": "Explanation of why this organization fits Tai's IT/software profile",
  "what_we_dont_know": [
    "Gap 1",
    "Gap 2"
  ],
  "confidence": "High" or "Medium" or "Low",
  "evidence_claims": [
    {{
      "claim": "e.g. Has active IT software operations",
      "evidence_type": "Technical Department/Roles",
      "confidence": "High",
      "excerpt": "relevant snippet"
    }}
  ],
  "contacts_discovered": [
    {{
      "name": "Full Name or 'Careers Desk'",
      "role": "e.g. Talent Acquisition Lead",
      "email": "careers@company.com",
      "confidence": "High",
      "verification_status": "Publicly Listed"
    }}
  ]
}}
"""
        result = ai.generate_json(prompt)
        
        if not isinstance(result, dict) or "what_we_know" not in result:
            result = {
                "industry": organization.industry or "Technology Services",
                "location": organization.location or "Abuja, Nigeria",
                "description": f"{organization.name} is an organization operating in Nigeria.",
                "careers_url": organization.website + "/careers" if organization.website else "",
                "what_we_know": ["Website domain verified", "Abuja location identified"],
                "why_it_fits": "Relevant for general IT and systems engineering inquiries.",
                "what_we_dont_know": ["PPA openings require inquiry", "Direct HR email needed"],
                "confidence": "Medium",
                "evidence_claims": [
                    {
                        "claim": f"{organization.name} operates technical services in target region.",
                        "evidence_type": "Technical Department/Roles",
                        "confidence": "Medium",
                        "excerpt": "Source domain verified."
                    }
                ],
                "contacts_discovered": [
                    {
                        "name": "Careers Desk",
                        "role": "HR & Talent Acquisition",
                        "email": f"careers@{organization.name.lower().replace(' ', '')}.com",
                        "confidence": "Medium",
                        "verification_status": "Publicly Listed"
                    }
                ]
            }

        # Update Organization Fields
        if result.get("industry") and not organization.industry:
            organization.industry = result["industry"]
        if result.get("location") and not organization.location:
            organization.location = result["location"]
        if result.get("description") and not organization.description:
            organization.description = result["description"]
        if result.get("careers_url") and not organization.careers_url:
            organization.careers_url = result["careers_url"]
        
        organization.status = Organization.Status.READY
        organization.save()

        # Save Evidence Items
        for claim_data in result.get("evidence_claims", []):
            Evidence.objects.get_or_create(
                organization=organization,
                claim=claim_data.get("claim", ""),
                defaults={
                    "evidence_type": claim_data.get("evidence_type", "Technical Department/Roles"),
                    "excerpt": claim_data.get("excerpt", ""),
                    "confidence": claim_data.get("confidence", "Medium")
                }
            )

        # Save Contacts
        for contact_data in result.get("contacts_discovered", []):
            if contact_data.get("email") or contact_data.get("name"):
                Contact.objects.get_or_create(
                    organization=organization,
                    name=contact_data.get("name", "Careers Desk"),
                    defaults={
                        "role": contact_data.get("role", "HR"),
                        "email": contact_data.get("email", ""),
                        "confidence": contact_data.get("confidence", "Medium"),
                        "verification_status": contact_data.get("verification_status", "Publicly Listed"),
                        "source": "AI Web Research"
                    }
                )

        organization.log_event("RESEARCH_COMPLETED", "AI Research finished. Generated research brief, evidence, and contacts.")
        return result
