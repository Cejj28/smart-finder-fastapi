# Smart Finder — FastAPI Analytics Service

## Overview

This is the **read-only analytics microservice** for the Smart Finder system.  
It connects to the **same shared PostgreSQL database** managed by the Django backend and exposes aggregated statistics endpoints for the web dashboard.

> **Django** is the primary backend — it owns all data, migrations, and authentication.  
> **FastAPI** reads from Django's tables to power analytics charts.

---

## Endpoints

| Method | Path | Description | Auth Required |
|--------|------|-------------|:---:|
| `GET` | `/` | Service info | No |
| `GET` | `/health` | Health check + DB ping | No |
| `GET` | `/docs` | Swagger UI | No |
| `GET` | `/stats/overview` | Totals: items, users, status counts | ✅ |
| `GET` | `/stats/by-type` | Count of Lost vs Found | ✅ |
| `GET` | `/stats/by-status` | Count per status | ✅ |
| `GET` | `/stats/by-location` | Top 10 locations | ✅ |
| `GET` | `/stats/trends` | Items per day (last 30 days) | ✅ |
| `GET` | `/stats/recent` | Last 5 reported items | ✅ |

**Auth**: Pass your Django token in the header:  
```
Authorization: Token <your-django-token>
```
FastAPI verifies this directly against the shared `authtoken_token` table — no separate login needed.

---

## Local Development

### 1. Create a virtual environment
```bash
cd smart-finder-fastapi
python -m venv venv
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Set environment variables
```bash
copy .env.example .env   # Windows
cp .env.example .env     # macOS/Linux
```

Edit `.env` and set `DATABASE_URL` to your local PostgreSQL or the Render Internal DB URL.

> **Local dev tip**: You can use SQLite URL format for testing: `sqlite+aiosqlite:///./test.db`  
> But for full compatibility, point to the same PostgreSQL used by Django.

### 4. Run the server
```bash
uvicorn main:app --reload --port 8001
```

Open [http://localhost:8001/docs](http://localhost:8001/docs) to test all endpoints interactively.

---

## Project Structure

```
smart-finder-fastapi/
├── main.py           # FastAPI app, CORS, router registration
├── database.py       # Async SQLAlchemy engine + session
├── models.py         # SQLAlchemy models mirroring Django's tables
├── schemas.py        # Pydantic response schemas
├── auth.py           # Django token verification dependency
├── routers/
│   ├── __init__.py
│   ├── health.py     # GET /health
│   └── analytics.py  # GET /stats/*
├── requirements.txt
├── .env.example
└── .gitignore
```

---

## Deployment on Render

See the root `render.yaml` for the full deployment spec. Quick summary:

1. Push code to GitHub.
2. On [render.com](https://render.com), click **New → Blueprint** and select the repo root.
3. Render reads `render.yaml` and creates all services automatically.
4. After the first deploy, get the **Internal Database URL** from the Render PostgreSQL dashboard and verify it's injected as `DATABASE_URL` into both services.
5. Visit `https://smart-finder-fastapi.onrender.com/docs` to verify the API is live.

---

## Database Notes

- ⚠️ FastAPI does **NOT** run any migrations. Django owns the schema.
- Always run `python manage.py migrate` on the Django service first.  
- FastAPI's SQLAlchemy models are read-only mirrors — they match Django's table names exactly (`api_item`, `auth_user`, `authtoken_token`).
