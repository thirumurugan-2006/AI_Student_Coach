# AI Career Coach — Backend

> **AI-Native Personalized Career Coach & Interview Preparation System**
>
> A privacy-first, AI-powered career coaching platform built with FastAPI and Groq.

---

## Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [API Reference](#api-reference)
- [Project Structure](#project-structure)
- [Configuration](#configuration)
- [Development](#development)
- [Testing](#testing)

---

## Overview

The AI Career Coach backend provides an intelligent coaching engine that helps students and junior engineers prepare for software engineering careers. It uses a **Groq LLM** for all AI features.

### Features

| Feature | Endpoint | Description |
|---------|----------|-------------|
| Career Discovery Survey | `POST /survey/` | Profiles the student's goals and background |
| Adaptive Assessment | `POST /assessment/` | Tests technical knowledge dynamically |
| Learning Roadmap | `POST /learning/` | Generates personalised study plans |
| Mock Interviews | `POST /interview/` | Simulates recruiter interviews |
| Self-Reflection | `POST /reflection/` | Tracks confidence and growth |
| Dashboard | `GET /dashboard/` | Shows progress and readiness score |
| Career Coach Chat | `POST /coach/chat` | Unified coach interaction |

---

## Architecture

```
Frontend
   ↓ REST API
FastAPI (main.py)
   ↓
API Layer (api/)
   ↓
Career Coach Orchestrator (agent/career_coach.py)
   ↓
Skill Registry → Skill Execution
   ↓
LLM Interface → Groq
   ↓
Evaluation Engine → Student Memory → Database
```

**Key Design Principles:**
- Career Coach is the **sole orchestrator** — skills never control workflow
- Skills **never evaluate** — all scoring goes through the Evaluation Engine
- Student Memory is the **single source of truth** for all student state
- All LLM calls go through **LLMInterface only** — never call the provider directly

---

## Prerequisites

| Requirement | Version |
|-------------|---------|
| Python | 3.11+ |
| Groq | Latest |
| llama3-8b-8192 model | via Groq API |

---

## Quick Start

### 1. Clone and set up environment

```bash
cd backend
python -m venv venv
venv\Scripts\activate          # Windows
source venv/bin/activate        # Linux / macOS
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure environment

```bash
cp .env.example .env
# Edit .env with your settings
```

### 4. Configure environment

```bash
cp .env.example .env
# Add your GROQ_API_KEY to .env
```

### 5. Run the backend

```bash
uvicorn main:app --reload --port 8000
```

### 6. Open API docs

Visit: [http://localhost:8000/docs](http://localhost:8000/docs)

---

## API Reference

### Authentication

Most endpoints accept a `user_id` query parameter or require a JWT Bearer token.

```bash
# Get a token via signup
curl -X POST http://localhost:8000/user/signup \
  -H "Content-Type: application/json" \
  -d '{"name": "Alice", "email": "alice@example.com"}'
```

Response includes `access_token` — use it as `Authorization: Bearer <token>`.

### Core Endpoints

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| `GET` | `/` | No | API info |
| `GET` | `/health` | No | Health check |
| `GET` | `/docs` | No | Swagger UI |
| `POST` | `/user/signup` | No | Sign up or log in |
| `GET` | `/user/profile` | No | Get user profile |
| `POST` | `/survey/` | user_id param | Run career survey |
| `POST` | `/assessment/` | user_id param | Run assessment |
| `POST` | `/learning/` | JWT | Generate learning roadmap |
| `POST` | `/interview/` | user_id param | Start mock interview |
| `POST` | `/reflection/` | user_id param | Submit reflection |
| `GET` | `/dashboard/` | JWT | Get student dashboard |
| `POST` | `/coach/chat` | JWT | Unified coach chat |
| `GET` | `/coach/skills` | No | List available skills |
| `GET` | `/coach/status` | No | Agent status |

---

## Project Structure

```
backend/
├── main.py                    # FastAPI app + lifespan
├── requirements.txt
├── .env                       # Local config (gitignored)
├── .env.example               # Config template
│
├── api/                       # REST endpoints
│   ├── router.py              # Centralised router registration
│   ├── user.py
│   ├── survey.py
│   ├── assessment.py
│   ├── learning.py
│   ├── interview.py
│   ├── reflection.py
│   ├── dashboard.py
│   └── career_coach.py
│
├── core/                      # Framework core
│   ├── constants.py           # App-wide constants
│   ├── dependencies.py        # FastAPI DI
│   ├── exceptions.py          # Custom exceptions + handlers
│   ├── security.py            # Password + JWT utilities
│   ├── logger.py              # Structured logging
│   ├── base_skill.py          # Skill base class
│   ├── llm_interface.py       # LLM abstraction
│   ├── prompt_loader.py       # Markdown prompt loader
│   ├── context_builder.py     # Prompt context formatter
│   ├── validator.py           # Output validator
│   └── retry.py               # Retry decorator
│
├── config/
│   └── settings.py            # Pydantic settings
│
├── database/
│   ├── base.py                # SQLAlchemy Base
│   ├── session.py             # Async engine + session
│   ├── init_db.py             # Table creation
│   └── seed.py                # Test data seeder
│
├── models/                    # SQLAlchemy ORM models
├── repositories/              # Repository pattern (CRUD)
│
├── agent/
│   ├── career_coach.py        # Main orchestrator
│   └── registry.py            # Skill registry
│
├── memory/
│   ├── student_memory.py      # In-memory student state
│   ├── knowledge_graph.py     # Knowledge graph manager
│   └── memory_store.py        # Memory utilities
│
├── evaluation/
│   ├── evaluation_engine.py   # Central evaluation processor
│   ├── confidence.py
│   ├── readiness.py
│   └── progress.py
│
├── services/
│   ├── groq_service.py      # Groq HTTP client
│   ├── memory_service.py      # DB ↔ memory sync
│   ├── recommendation_service.py
│   └── student_service.py
│
├── skills/
│   ├── survey/
│   ├── assessment/
│   ├── learning/
│   ├── interview/
│   └── reflection/
│
├── auth/
│   ├── jwt_handler.py
│   ├── password_handler.py
│   └── dependencies.py
│
├── prompts/                   # LLM prompt markdown files
├── utils/                     # Shared utilities
├── uploads/                   # File upload directories
└── tests/                     # Test suite
```

---

## Configuration

Copy `.env.example` to `.env` and update:

```env
# Database (SQLite for development)
DATABASE_URL=sqlite+aiosqlite:///./data/career_coach.db

# Security — CHANGE THIS IN PRODUCTION
SECRET_KEY=your-secret-key-here-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60

# Groq
LLM_PROVIDER=groq
GROQ_API_KEY=your-groq-api-key
GROQ_MODEL=llama3-8b-8192
GROQ_TIMEOUT=60
GROQ_TEMPERATURE=0.3

# Debug
DEBUG=True
```

---

## Development

### Database migrations (Alembic)

```bash
# Auto-generate a migration after model changes
alembic revision --autogenerate -m "describe change"

# Apply migrations
alembic upgrade head

# Rollback one step
alembic downgrade -1
```

### Seed the database

```bash
python -m database.seed
```

### Logging

Logs are output to stdout. Key loggers:

| Logger | Module |
|--------|--------|
| `career_coach.api` | API layer |
| `career_coach.database` | Database operations |
| `career_coach.auth` | Authentication |

---

## Testing

```bash
# Run all tests
pytest tests/ -v

# Run specific test module
pytest tests/api/test_user.py -v

# Run with coverage
pytest tests/ --cov=. --cov-report=term-missing

# Run only async tests
pytest tests/ -v -k "asyncio"
```

> **Note:** All tests use an in-memory SQLite database and mock the LLM service.
> No real Groq key or PostgreSQL instance is required for tests.

---

## Security Notes

1. Change `SECRET_KEY` before deploying to production
2. Set `DEBUG=False` in production
3. Update `ALLOWED_ORIGINS` to your frontend domain
4. Use PostgreSQL (`asyncpg`) in production, not SQLite
5. Run behind a reverse proxy (nginx) in production

---

## License

MIT License — See root `LICENSE` file for details.
