"""
main.py — FastAPI Application Entry Point
AI for Account Intelligence Platform
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.config import settings
from app.database import engine, Base
from app.api.endpoints import router as api_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan: startup and shutdown events."""
    # Startup: create DB tables
    print("🚀 Starting AI for Account Intelligence...")
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables verified/created")
    yield
    # Shutdown
    print("🛑 Shutting down...")


app = FastAPI(
    title="AI for Account Intelligence",
    description=(
        "Plataforma de Account Intelligence 360° con Early Warning System Comercial. "
        "Analiza empresas, detecta señales de compra y genera speech comercial automático."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# ── CORS ──────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ───────────────────────────────────────────────────────────────────
app.include_router(api_router, prefix=settings.API_PREFIX)


@app.get("/", tags=["Health"])
def root():
    return {
        "service": "AI for Account Intelligence",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
    }


@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "healthy"}
