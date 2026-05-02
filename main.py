from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from database import engine, Base
from routers import analytics, health, predict

@asynccontextmanager
async def lifespan(app: FastAPI):
    # FastAPI reads from Django's shared DB — no table creation needed here.
    # Django owns all migrations. We just open and close the connection pool.
    async with engine.begin() as conn:
        # Verify connection on startup
        pass
    yield


app = FastAPI(
    title="Smart Finder Analytics API",
    description=(
        "Read-only analytics service for Smart Finder. "
        "Reads from the shared PostgreSQL database managed by Django. "
        "Use the Django backend at /api for all CRUD and authentication."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# CORS — allow requests from the web frontend (set FRONTEND_URL in env for production)
import os
FRONTEND_URL = os.getenv("FRONTEND_URL", "*")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_URL] if FRONTEND_URL != "*" else ["*"],
    allow_credentials=True,
    allow_methods=["GET"],   # Analytics is read-only
    allow_headers=["*"],
)

app.include_router(health.router, tags=["Health"])
app.include_router(analytics.router, prefix="/stats", tags=["Analytics"])
app.include_router(predict.router, tags=["Machine Learning"])

@app.get("/", tags=["Root"])
async def root():
    return {
        "service": "Smart Finder Analytics API",
        "version": "1.0.0",
        "docs": "/docs",
        "stats": "/stats/overview",
    }
