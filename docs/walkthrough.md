# Walkthrough — Personal AI-Powered NYSC PPA Hunting Workspace

This document provides a comprehensive walkthrough of the built, verified, and delivered **Personal AI-Powered NYSC PPA Hunting Workspace** ("Tai's PPA Desk").

---

## 🌟 Delivered Features & Workflows

### 1. Mobile-First Editorial Design System
- **Visual Aesthetic**: Designed as a refined research workstation (`Newsreader` serif for headings, `Plus Jakarta Sans` for labels, and `JetBrains Mono` for metadata).
- **Mobile Navigation**: Dedicated bottom navigation bar on mobile screen sizes (`< 768px`) with instant thumb access to Today, Orgs, Quick Capture, Outreach, and Profile.
- **PWA Capabilities**: Service worker (`static/sw.js`), app manifest (`static/manifest.json`), and offline local note draft preservation in `static/js/app.js`.

### 2. "Today" Action Desk (`core`)
- Prioritizes urgent follow-ups, pending research reviews, ready-to-contact organizations, and recently discovered companies.
- Displays recommended next actions with explainable reasons ("Why?").

### 3. Organization Lifecycle & Workstation (`organizations`)
- Organization states: `Discovered`, `Researching`, `Ready to Contact`, `Contacted`, `Awaiting Response`, `Follow Up Due`, `In Discussion`, `Positive`, `Declined`, `Closed`.
- **Quick Capture Drawer**: Paste company name & URL to instantly save and trigger background research.
- **Explainable Next Action Engine**: Automatically calculates the single best next action for each organization (e.g. "Run Research", "Find Contacts", "Draft Outreach", "Send Follow-up").
- **Notes & Activity Timeline**: Chronological event logging for every note, research trigger, contact creation, and outreach status update.

### 4. Background AI Research Engine (`research` & `ai`)
- Web fetcher (`httpx` + `BeautifulSoup4`) with prompt injection protection (treating external HTML strictly as untrusted data).
- Abstract search provider (`Tavily` + fallback `MockSearchProvider`).
- Celery + Redis background tasks with synchronous fallback execution.
- **AI Research Brief**: Summarizes "What We Know", "Why It Fits", "What We Don't Know", evidence claims with confidence provenance, and discovered contacts.

### 5. Contact Management & Deduplication (`contacts`)
- Verification status tracking (`Verified`, `Publicly Listed`, `Provider Sourced`, `Unverified`).
- Deduplication engine identifying matching emails or names to prevent duplicate HR records.

### 6. Outreach Intelligence & Follow-up Engine (`outreach`)
- **Authentic Nigerian Professional English AI Drafter**: Tailors outreach emails to Tai's profile (Computer Engineering, Python/Django, Linux) and extracted company evidence (avoiding generic AI buzzwords).
- Quick copy and `mailto:` client opener.
- **5-Day Follow-Up Calculator**: Automatically sets follow-up reminders and feeds into the Today action desk.

### 7. Browser Extension Capture API (`core`)
- `/api/v1/capture/` JSON endpoint for browser bookmarklet and extension integration.

---

## 🧪 Verification & Test Results

### 1. Django System Checks
```bash
python3 manage.py check
# Result: System check identified no issues (0 silenced).
```

### 2. Automated Test Suite
Ran `python3 manage.py test`:
```text
Ran 4 tests in 40.213s
OK
```
- Verified organization quick capture and timeline event creation.
- Verified contact deduplication engine.
- Verified browser capture API endpoint (`/api/v1/capture/`).

---

## 🚀 How to Run

```bash
# Initialize single user account (tai / taipassword)
python3 manage.py setup_user

# Run local server
python3 manage.py runserver 8000
```
Open `http://localhost:8000` in your browser or mobile phone (Credentials: `tai` / `taipassword`).
