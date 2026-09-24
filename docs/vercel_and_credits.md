# Vercel Deployment & Free Tier API Protection Guide

---

## ⚡ 1. API Credit Conservation Strategy (Free Tier Protection)

To prevent exhausting your free tier quotas on Gemini, Tavily, Hunter, or RocketReach:

1. **24-Hour Result Caching**: Search queries and web fetch results are cached in Django's caching layer (`django.core.cache`) for 86,400 seconds (24 hours). Re-searching or visiting an organization multiple times uses cached results instead of calling the API.
2. **Search Result Cap**: Search queries are capped at **3 results per query** (instead of 10+) to minimize payload usage per API call.
3. **Lazy AI Invocation**: AI research briefs and outreach drafts are generated only when explicitly triggered by user action, avoiding automatic background consumption loops.
4. **Untrusted Content Trimming**: HTML content is cleaned and trimmed to 4,000 characters before sending to Gemini, preserving prompt token limits.

---

## 🌐 2. Deploying to Vercel

### Is Vercel Feasible for this Project?
**Yes!** Vercel can host the Django web application via Python Serverless Functions (`@vercel/python`).

### Important Feasibility Considerations:
1. **Database**: SQLite will reset on every serverless function invocation on Vercel. For Vercel deployment, connect a free PostgreSQL database like **Supabase** or **Neon** by setting `DATABASE_URL` in Vercel's Environment Variables.
2. **Background Workers (Celery/Redis)**: Vercel serverless functions time out after 10-60 seconds and do **not** run persistent background worker daemons. On Vercel, the application automatically catches Celery connection errors and runs research jobs synchronously inline within the request.

---

### Steps to Deploy on Vercel:

#### Step 1: Install Vercel CLI & Login
```bash
npm install -g vercel
vercel login
```

#### Step 2: Push Code to GitHub / Git Provider
Ensure `vercel.json` and `nysc_workspace/wsgi.py` are committed to your repository.

#### Step 3: Deploy via Vercel CLI or Dashboard
```bash
# Run inside project directory
vercel
```

#### Step 4: Configure Vercel Environment Variables
In the Vercel Dashboard project settings (**Settings -> Environment Variables**), add:
- `DEBUG` = `False`
- `SECRET_KEY` = `<your-production-secret-key>`
- `DATABASE_URL` = `postgres://...` (from Supabase or Neon)
- `GEMINI_API_KEY` = `<your-gemini-key>`
- `TAVILY_API_KEY` = `<your-tavily-key>`
- `CSRF_TRUSTED_ORIGINS` = `https://<your-vercel-app>.vercel.app`

---

## 🚀 Recommended Alternative: Render.com or Railway.app (Free Tier)

If you want persistent **Celery background workers** and **Redis** alongside Django without serverless timeout limits:
- **Render.com**: Offers a free Web Service + free PostgreSQL + free Redis instance.
- **Railway.app**: Offers free trial credits to run Django, Celery, and Postgres in Docker.
