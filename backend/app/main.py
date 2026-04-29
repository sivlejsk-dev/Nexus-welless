"""Nexus Wellness Platform — FastAPI application entry point."""

from contextlib import asynccontextmanager

import structlog
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware

from app.core.config import settings
from app.routers import astrology, auth, detox, meditation, nexus, nutrition, users, voice

log = structlog.get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Auto-create tables on startup (dev convenience; use Alembic in production)
    from app.db.base import engine, Base
    from app.models.user import User, WellnessProfile, MeditationSession, DetoxLog  # noqa: F401
    from app.models.session import ChatSession, ChatTurn  # noqa: F401
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Seed ChromaDB domain knowledge (idempotent)
    try:
        from app.services.knowledge_seeder import knowledge_seeder
        counts = knowledge_seeder.seed_all()
        if not counts.get("skipped"):
            log.info("nexus_wellness.knowledge_seeded", counts=counts)
    except Exception as exc:
        log.warning("nexus_wellness.knowledge_seed_failed", error=str(exc))

    log.info("nexus_wellness.startup", environment=settings.environment)
    yield
    log.info("nexus_wellness.shutdown")


app = FastAPI(
    title="Nexus Wellness Platform",
    description="AI-driven mind, body, and spirit wellness — powered by Nexus.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# ── Middleware ────────────────────────────────────────────────────────────────

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(GZipMiddleware, minimum_size=1000)

# ── Routers ───────────────────────────────────────────────────────────────────

API_PREFIX = "/api/v1"

app.include_router(auth.router, prefix=API_PREFIX)
app.include_router(users.router, prefix=API_PREFIX)
app.include_router(meditation.router, prefix=API_PREFIX)
app.include_router(nutrition.router, prefix=API_PREFIX)
app.include_router(astrology.router, prefix=API_PREFIX)
app.include_router(detox.router, prefix=API_PREFIX)
app.include_router(nexus.router, prefix=API_PREFIX)
app.include_router(voice.router, prefix=API_PREFIX)


# ── Health check ─────────────────────────────────────────────────────────────

@app.get("/health", tags=["system"])
async def health():
    return {"status": "ok", "version": "1.0.0", "environment": settings.environment}


@app.get("/", tags=["system"])
async def root():
    return {
        "name": "Nexus Wellness Platform API",
        "version": "1.0.0",
        "docs": "/docs",
        "modules": ["auth", "users", "meditation", "nutrition", "astrology", "detox", "nexus-ai"],
    }
