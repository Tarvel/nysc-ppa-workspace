from .provider import get_ai_provider
from accounts.models import UserProfile
from organizations.models import Organization
from contacts.models import Contact

class OutreachDrafter:
    """Drafts evidence-aware outreach in authentic Nigerian professional English."""
    
    @staticmethod
    def draft_initial_outreach(organization: Organization, contact: Contact = None, profile: UserProfile = None) -> dict:
        ai = get_ai_provider()
        
        recipient_name = contact.name if contact else "Hiring Manager / Careers Desk"
        recipient_email = contact.email if contact else organization.general_email
        
        # Check evidence
        nysc_evidence = organization.evidence_items.filter(evidence_type='NYSC Acceptance Evidence').exists()
        has_vacancies = organization.opportunities.exists()

        prompt = f"""
Draft a concise, authentic Nigerian professional English outreach email inquiring about NYSC PPA placement.

USER PROFILE:
- Name: Tai
- Education: {profile.education if profile else 'Computer Engineering'}
- Skills: {profile.skills if profile else 'Python, Django, FastAPI, PostgreSQL, Linux'}
- Preferred Location: {profile.preferred_locations if profile else 'Abuja'}
- NYSC Batch: {profile.nysc_batch if profile else '2026 Batch A'}

ORGANIZATION INFO:
- Name: {organization.name}
- Industry: {organization.industry or 'Technology / Services'}
- Location: {organization.location}
- Has NYSC Evidence: {nysc_evidence}
- Has Specific Vacancies Listed: {has_vacancies}
- Recipient: {recipient_name} ({contact.role if contact else 'HR'})

RULES:
1. Avoid generic AI fluff ("esteemed organization", "keen interest", "hope this email finds you well").
2. Direct, professional Nigerian business tone.
3. Keep subject line punchy (e.g. "NYSC PPA Inquiry — IT & Backend Engineering | Tai").
4. If no explicit vacancy evidence exists, ask whether they consider Corps Members for IT/technical roles.
5. If evidence exists, reference previous Corps Member activities appropriately.
6. Max 150 words.

Return JSON format:
{{
  "subject": "...",
  "message": "..."
}}
"""
        result = ai.generate_json(prompt)
        if isinstance(result, dict) and "subject" in result and "message" in result:
            return result

        # Fallback template
        if nysc_evidence:
            intro = f"I came across your organization's previous recruitment activity involving Corps Members and wanted to reach out regarding NYSC PPA placement."
        else:
            intro = f"I am reaching out to ask whether {organization.name} considers Corps Members for IT or software engineering PPA placements in {organization.location or 'Abuja'}."

        subject = f"NYSC PPA Inquiry — IT / Backend Engineering — Tai"
        message = (
            f"Dear {recipient_name},\n\n"
            f"{intro}\n\n"
            f"I am a Computer Engineering graduate with experience in Python, Django, PostgreSQL, and Linux systems administration. "
            f"I am looking for a technical PPA role where I can contribute to your engineering operations during my service year.\n\n"
            f"I have attached my CV for your review. Please let me know if there is an avenue to submit a formal application or discuss potential opportunities.\n\n"
            f"Thank you for your time and consideration.\n\n"
            f"Best regards,\n"
            f"Tai"
        )
        return {"subject": subject, "message": message}
