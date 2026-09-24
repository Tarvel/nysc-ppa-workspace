# Tai's Personal AI-Powered NYSC PPA Hunting Workspace

A private, single-user research workstation designed to streamline, track, and manage your NYSC PPA search. Eliminates tab chaos by capturing organizations, running background web research, generating evidence-based research briefs, deduplicating contacts, and drafting authentic Nigerian professional English outreach.

---

## 🚀 Features

- **Genuinely Mobile-First**: Built for usage from mobile phones (e.g. during NYSC camp) with bottom navigation, touch drawers, floating quick capture sheets, and responsive touch feedback (`scale(0.97)`).
- **"Today" Action Center**: Answers *"What should I do right now?"* by surfacing urgent follow-ups, pending research reviews, ready-to-contact organizations, and recommended next steps.
- **Editorial Research Workstation**: High-density typography design system using `Newsreader` serif, `Plus Jakarta Sans`, and `JetBrains Mono` for a calm, professional research desk experience.
- **Evidence-Based AI Engine**: Uses Gemini API with structured JSON schemas (and mock fallback) to extract evidence claims with confidence provenance. Zero hallucinated vacancy claims.
- **Next Action Engine**: Recommends the single most logical next step for every organization with clear explainability ("Why?").
- **Contact Deduplication & Provenance**: Normalizes HR and talent acquisition contact routes, highlighting provenance and duplicate warnings.
- **Outreach & Follow-Up Engine**: Drafts tailored Nigerian professional English emails based on Tai's profile and extracted evidence. Manages follow-up reminders and status workflows.
- **Browser Capture API**: Endpoint `/api/v1/capture/` for bookmarklets or web extension integration.
- **PWA Ready**: Service worker (`sw.js`), web app manifest (`manifest.json`), and local draft caching for offline note taking.

---

## 🛠 Tech Stack

- **Backend**: Python 3.13, Django 4.2+, PostgreSQL / SQLite
- **Async Tasks**: Celery + Redis (with synchronous fallback)
- **Frontend**: Django Templates + Tailwind CSS + HTMX + Alpine.js
- **AI Integration**: Google Gemini API (`google-genai` / HTTP structured output)
- **Scraping & Research**: HTTPX + BeautifulSoup4 + Tavily / Brave Search API

---

## 🚀 Getting Started

### 1. Local Development Setup (Quickstart)

```bash
# 1. Clone or navigate to project directory
cd /home/tai/Documents/Django_Projects/nysc

# 2. Copy environment variables
cp .env.example .env

# 3. Create database migrations & apply
python3 manage.py migrate

# 4. Initialize single user (tai / taipassword)
python3 manage.py setup_user

# 5. Start development server
python3 manage.py runserver 8000
```

Access the app at `http://localhost:8000`.

### 2. Docker Setup

```bash
docker-compose up --build
```

---

## 🔌 Browser Extension / Bookmarklet Capture API

You can capture any web page while browsing by sending a `POST` request to `/api/v1/capture/`:

```json
{
  "url": "https://company.com/careers",
  "title": "Careers at Company X",
  "selected_text": "We welcome NYSC corps members for IT & software engineering roles in Abuja.",
  "organization_name": "Company X"
}
```

---

## 🧪 Running Tests

```bash
python3 manage.py test
```

---

## 📄 License
Private Personal Tool for Tai. All rights reserved.
