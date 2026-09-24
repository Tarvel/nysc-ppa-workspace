import os
import json
from typing import Protocol, Dict, Any, Optional

class AIProvider(Protocol):
    def generate_json(self, prompt: str, schema: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        ...
    def generate_text(self, prompt: str) -> str:
        ...

class GeminiAIProvider:
    def __init__(self, api_key: str):
        self.api_key = api_key

    def generate_text(self, prompt: str) -> str:
        try:
            from google import genai
            client = genai.Client(api_key=self.api_key)
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt
            )
            return response.text
        except Exception as e:
            print(f"Gemini API Error: {e}")
            return f"AI Generation Failed: {e}"

    def generate_json(self, prompt: str, schema: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        full_prompt = f"{prompt}\n\nIMPORTANT: Respond with VALID JSON ONLY. Do not include markdown formatting or backticks around the JSON."
        text = self.generate_text(full_prompt)
        text = text.strip()
        if text.startswith("```json"):
            text = text[7:]
        if text.startswith("```"):
            text = text[3:]
        if text.endswith("```"):
            text = text[:-3]
        text = text.strip()
        try:
            return json.loads(text)
        except Exception as e:
            print(f"JSON Parse Error: {e}, Content: {text}")
            return {"error": "Failed to parse AI JSON response", "raw": text}

class MockAIProvider:
    """Mock provider when GEMINI_API_KEY is not set."""
    def generate_text(self, prompt: str) -> str:
        if "outreach" in prompt.lower() or "email" in prompt.lower():
            return (
                "Dear Hiring Manager / HR Team,\n\n"
                "I hope this message finds you well.\n\n"
                "I am a Computer Engineering graduate reaching out to inquire whether your organization "
                "currently accepts NYSC Corps Members for IT, software engineering, or technical PPA placements.\n\n"
                "My technical background includes backend development with Python, Django, PostgreSQL, and Linux systems administration. "
                "I would appreciate the opportunity to contribute to your technical team during my service year.\n\n"
                "Thank you for your time and consideration. I look forward to hearing from you.\n\n"
                "Best regards,\n"
                "Tai"
            )
        return "Mock AI response generated for testing."

    def generate_json(self, prompt: str, schema: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        prompt_lower = prompt.lower()
        if "brief" in prompt_lower or "research" in prompt_lower:
            return {
                "what_we_know": [
                    "Official company website & careers page verified",
                    "Target location presence confirmed (Abuja / Nigeria)",
                    "Active technical & IT operations identified"
                ],
                "why_it_fits": "Strong technical alignment with your Python, Django, Linux & systems background.",
                "what_we_dont_know": [
                    "No explicit public vacancy posting for NYSC PPA corps members found",
                    "Direct HR lead email address requires verification"
                ],
                "confidence": "Medium",
                "evidence_claims": [
                    {
                        "claim": "Company maintains an active IT and engineering division",
                        "evidence_type": "Technical Department/Roles",
                        "confidence": "High"
                    }
                ],
                "contacts_discovered": [
                    {
                        "name": "HR & Careers Desk",
                        "role": "Talent Acquisition",
                        "email": "careers@example.com",
                        "confidence": "Medium",
                        "verification_status": "Publicly Listed"
                    }
                ],
                "next_action": "Send a general NYSC PPA inquiry to careers desk asking if corps members are accepted.",
                "next_action_why": "The company has an IT department, but no active PPA vacancy post is listed."
            }
        return {"result": "Mock JSON response"}

def get_ai_provider() -> AIProvider:
    key = os.getenv("GEMINI_API_KEY")
    if key:
        return GeminiAIProvider(key)
    return MockAIProvider()
