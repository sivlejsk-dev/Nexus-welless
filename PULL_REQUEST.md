# Nexus Wellness Platform — Skeleton

## Summary

Establishes the full monorepo skeleton for the Nexus Wellness Platform: a modular, AI-driven wellness app integrating mind, body, and spirit. The Nexus/Celestal-Eye AI engine is integrated as the core intelligence layer, producing real astronomical calculations, personalized daily guides, and wellness interpretations — not mocks.

**20/20 API integration tests passing. Both servers running.**

---

## Architecture

```
nexus-wellness/
├── frontend/          Next.js 14 (App Router, Tailwind, TypeScript)
├── backend/           FastAPI + async SQLAlchemy (Python 3.12)
│   └── app/
│       ├── nexus_core/    ← Real Celestal-Eye source modules
│       ├── routers/       ← 7 modular API routers
│       ├── services/      ← Business logic per module
│       ├── models/        ← SQLAlchemy ORM (User, Profile, Sessions, Logs)
│       └── schemas/       ← Pydantic request/response schemas
└── docker-compose.yml     FastAPI + Next.js + PostgreSQL 16 + Redis 7
```

---

## Modules Built

| Module | Backend endpoints | Frontend page |
|---|---|---|
| **Auth** | `POST /auth/register`, `/login`, `/refresh` | Login / register |
| **Users** | `GET/PUT /users/me/profile` | Profile page |
| **Meditation** | Guides, daily-guide, sessions, recommendations | Meditation page |
| **Nutrition** | Food search, healing foods, meal plans, recommendations | Nutrition page |
| **Astrology** | Birth chart, horoscopes, sign profiles, my-chart | Astrology page |
| **Detox** | Protocols, day guidance, logs, recommendations | Detox page |
| **Nexus AI** | `/nexus/recommend`, `/nexus/chat` | Nexus AI chat page |

**35 total API endpoints** — all documented at `/docs` (Swagger UI).

---

## Nexus Integration

The Celestal-Eye source modules are integrated at `backend/app/nexus_core/`:

| Module | What it powers |
|---|---|
| `BirthChartGenerator` | Real planetary positions (10 planets, aspects, houses) from birth date/time/location |
| `DailyAstrologer` | Personalized daily guidance keyed to the user's natal chart and today's date |
| `AstrologyInterpreter` | Full narrative chart interpretation (Sun, Moon, Rising, planets, life areas) |
| `guide_engine` | Maps 12 mental states × 5 goals → meditation style + breathing exercise + meal suggestions |

Every Nexus call has a graceful fallback — the app runs fully without an external API key.

The external Nexus LLM (`/nexus/recommend`, `/nexus/chat`) activates when `NEXUS_API_KEY` is set in `.env`.

---

## What's Needed Next

### Before going to production
- [ ] Set `NEXUS_API_KEY` in `.env` to activate LLM-powered recommendations
- [ ] Run `docker compose up -d` to switch from SQLite to PostgreSQL + Redis
- [ ] Run Alembic migrations: `alembic upgrade head`
- [ ] Set a strong `JWT_SECRET_KEY` in `.env`
- [ ] Configure `USDA_API_KEY` for live nutritional data (USDA FoodData Central)

### Module refinement (next iterations)
- [ ] **Nutrition** — expand healing foods database, integrate USDA live search, add macro tracking
- [ ] **Meditation** — add audio URLs, session streak tracking, Nexus-personalized script generation
- [ ] **Astrology** — expose transit forecasts, compatibility analysis, Vedic system (all in `nexus_core`)
- [ ] **Detox** — add symptom trend charts, protocol completion tracking, Nexus daily check-ins
- [ ] **Nexus AI** — connect full LLM chat with conversation history, voice input (audio modules in `nexus_core`)

### Infrastructure
- [ ] Add Redis caching for birth chart calculations and horoscopes
- [ ] Set up S3/GCS for user media storage (`STORAGE_BACKEND` in `.env`)
- [ ] Add rate limiting middleware
- [ ] Configure CI/CD pipeline

---

## Running Locally

```bash
# Backend
cd backend
pip install -r requirements.txt
DATABASE_URL="sqlite+aiosqlite:///./dev.db" uvicorn app.main:app --reload --port 8000

# Frontend
cd frontend
npm install
NEXT_PUBLIC_API_URL=http://localhost:8000 npm run dev

# Full stack (requires Docker)
cp .env.example .env   # fill in values
docker compose up -d
```

API docs: http://localhost:8000/docs
Frontend: http://localhost:3000
