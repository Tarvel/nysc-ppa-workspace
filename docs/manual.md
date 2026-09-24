# User & Administrator Operational Manual

This manual provides complete step-by-step instructions on running, configuring, deploying, and using **Tai's Personal AI-Powered NYSC PPA Hunting Workspace**.

---

## 📋 Prerequisites

- **Python**: Version 3.10+ (Tested on Python 3.13)
- **Docker & Docker Compose** (Optional, for containerized running)
- **Redis** (Optional, required if running Celery async background workers)
- **PostgreSQL** (Optional, defaults to SQLite for local development)

---

## ⚙️ Environment Configuration (`.env`)

Copy `.env.example` to `.env` in the root project directory:

```bash
cp .env.example .env
```

### Available Environment Variables:

| Variable | Default Value | Description |
| :--- | :--- | :--- |
| `DEBUG` | `True` | Run in development mode |
| `SECRET_KEY` | `django-insecure-...` | Django secret key |
| `ALLOWED_HOSTS` | `*` | Allowed host headers |
| `DATABASE_URL` | `sqlite:///db.sqlite3` | Database connection URI |
| `REDIS_URL` | `redis://localhost:6379/0` | Redis instance for cache & Celery backend |
| `CELERY_BROKER_URL` | `redis://localhost:6379/0` | Celery message broker URI |
| `GEMINI_API_KEY` | *(Empty)* | Google Gemini API key (Mock AI fallback enabled if empty) |
| `TAVILY_API_KEY` | *(Empty)* | Tavily Search API key (Mock Search fallback enabled if empty) |

---

## 🚀 Option 1: Running via Docker Compose (Recommended for Full Stack)

Docker Compose starts PostgreSQL, Redis, Django Web Server, and Celery Worker simultaneously.

### Steps:

```bash
# 1. Build and start containers in foreground
docker-compose up --build

# Or start in detached background mode
docker-compose up -d --build
```

### Container Services Launched:
- `db`: PostgreSQL 16 mapped to host port `5433:5432` (avoids local Postgres port 5432 conflict)
- `redis`: Redis 7 mapped to host port `6380:6379` (avoids local Redis port 6379 conflict)
- `web`: Django application on `http://localhost:8000` (auto-applies migrations & user setup)
- `worker`: Celery task worker processing background web research

---

## 💻 Option 2: Running Locally (Native Python Server)

### Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 2: Apply Database Migrations

```bash
python3 manage.py migrate
```

### Step 3: Create Single User Account (Tai)

```bash
python3 manage.py setup_user
```
*Creates user `tai` with default password `taipassword` and initializes Tai's PPA Profile.*

### Step 4: Start Development Server

```bash
python3 manage.py runserver 8000
```
Open `http://localhost:8000` in your browser.

---

## ⚙️ Option 3: Running Celery & Redis Background Tasks Locally

If you want background web research jobs to run asynchronously in a separate process:

### Terminal 1: Redis Server
```bash
redis-server
```

### Terminal 2: Celery Worker
```bash
celery -A nysc_workspace worker --loglevel=info
```

*Note: If Redis or Celery is not running, the application automatically catches the exception and executes research jobs synchronously without failing.*

---

## 📱 Mobile & NYSC Camp Usage (PWA)

The workspace is genuinely mobile-first:

1. Open `http://<your-server-ip>:8000` on your phone browser.
2. Tap **"Add to Home Screen"** or **"Install App"** in your mobile browser menu.
3. The app installs as a standalone PWA with bottom navigation, touch action sheets, and offline draft support for notes.

---

## 🔌 Browser Extension & Bookmarklet Capture API

You can capture web pages while browsing using the `/api/v1/capture/` endpoint:

### cURL Test Example:

```bash
curl -X POST http://localhost:8000/api/v1/capture/ \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://www.mainone.net/careers",
    "title": "MainOne Careers",
    "selected_text": "We welcome NYSC corps members for network and backend roles in Abuja.",
    "organization_name": "MainOne"
  }'
```

### Bookmarklet Code:

Create a browser bookmark with this URL:

```javascript
javascript:(function(){
  fetch('http://localhost:8000/api/v1/capture/', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({
      url: window.location.href,
      title: document.title,
      selected_text: window.getSelection().toString(),
      organization_name: document.title.split('-')[0].trim()
    })
  }).then(r => r.json()).then(d => alert(d.message)).catch(e => alert('Error capturing page'));
})();
```

---

## 🧪 Running Automated Tests

```bash
python3 manage.py test
```
