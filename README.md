# Nexus Wellness Platform

A modular, AI-driven wellness app integrating mind, body, and spirit — powered by the Nexus AI engine.

## Architecture

```
nexus-wellness/
├── frontend/          # Next.js 14 app (App Router)
├── backend/           # FastAPI service (Python 3.12)
├── docker-compose.yml # Local orchestration
└── docs/              # Architecture decisions
```

## Services

| Service    | Stack              | Port  |
|------------|--------------------|-------|
| Frontend   | Next.js 14         | 3000  |
| Backend    | FastAPI + Uvicorn  | 8000  |
| Database   | PostgreSQL 16      | 5432  |
| Cache      | Redis 7            | 6379  |

## Modules

- **Nexus AI** — Core intelligence engine (personalized recommendations)
- **Nutrition** — Food-as-medicine database, meal plans, nutritional analysis
- **Meditation** — Guided sessions, breathing exercises, mindfulness journeys
- **Detox** — Protocols, timelines, progress tracking
- **Astrology** — Birth charts, daily horoscopes, planetary transits
- **Auth** — JWT-based accounts, secure profile storage

## Quick Start

```bash
# Start all services
docker compose up -d

# Frontend only (dev)
cd frontend && npm run dev

# Backend only (dev)
cd backend && uvicorn app.main:app --reload --port 8000
```

## Environment Variables

Copy `.env.example` to `.env` and fill in your values:

```bash
cp .env.example .env
```
