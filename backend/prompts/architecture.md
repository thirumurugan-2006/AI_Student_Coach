# AI Career Coach — System Architecture

## Architecture Overview

```
Frontend (React / Next.js)
         ↓  HTTP REST
FastAPI Application (main.py)
         ↓
    API Layer (api/)
         ↓
  Career Coach Orchestrator (agent/career_coach.py)
         ↓
    Skill Registry (agent/registry.py)
         ↓
    Skill Execution (skills/<skill>/skill.py)
         ↓
    LLM Interface (core/llm_interface.py)
         ↓
    Ollama Service (services/ollama_service.py)
         ↓
    Ollama Server (llama3.2:3b)
         ↑
    Result flows back up
         ↓
   Evaluation Engine (evaluation/)
         ↓
    Student Memory (memory/student_memory.py)
         ↓
    Database (SQLite / PostgreSQL)
```

## Layer Responsibilities

### API Layer
- Receives HTTP requests
- Validates request payloads (Pydantic)
- Extracts student_id from JWT
- Delegates to Career Coach
- Returns JSON response

### Career Coach (Orchestrator)
- The ONLY component that decides what happens next
- Reads student memory
- Invokes the correct skill
- Sends results to Evaluation Engine
- Returns the final response to the API

### Skill Registry
- Dynamic registry of all skills
- Skills are registered at startup
- Executes skills by name (no if/else)

### Skills
- Isolated, single-responsibility components
- Each skill: loads instruction.md + examples.md, reads memory, builds prompt, calls LLM
- Skills return raw results — they do NOT evaluate or update memory

### LLM Interface
- Single point of contact for all LLM calls
- Wraps Ollama Service
- Handles retry, timeout, schema validation

### Evaluation Engine
- Processes skill results centrally
- Updates knowledge graph, readiness, confidence
- Writes updated state back to Student Memory

### Student Memory
- In-memory store for the active session
- Persisted to database via MemoryPersistenceService
- Single source of truth for all student state

## Module Map

```
backend/
├── main.py                    → FastAPI app, lifespan, route registration
├── config/settings.py         → All configuration via pydantic-settings
├── core/
│   ├── constants.py           → App-wide constants
│   ├── dependencies.py        → FastAPI dependency injection
│   ├── exceptions.py          → Custom exception classes + handlers
│   ├── logger.py              → Structured logging setup
│   ├── security.py            → Password hashing + JWT utilities
│   ├── base_skill.py          → BaseSkill abstract class
│   ├── llm_interface.py       → LLM abstraction layer
│   ├── prompt_loader.py       → Markdown prompt file loader
│   ├── context_builder.py     → Prompt context formatter
│   ├── validator.py           → Pydantic schema validator
│   └── retry.py               → Exponential backoff decorator
├── api/
│   ├── router.py              → Centralised router registration
│   ├── user.py                → User signup/profile
│   ├── survey.py              → Career survey
│   ├── assessment.py          → Technical assessment
│   ├── learning.py            → Learning roadmap
│   ├── interview.py           → Mock interview
│   ├── reflection.py          → Self-reflection
│   ├── dashboard.py           → Student dashboard
│   └── career_coach.py        → Generic coach chat endpoint
├── database/
│   ├── base.py                → SQLAlchemy declarative base
│   ├── session.py             → Async engine + session factory
│   └── init_db.py             → create_all_tables()
├── models/                    → SQLAlchemy ORM models
├── repositories/              → Repository pattern (CRUD)
├── agent/
│   ├── career_coach.py        → Main orchestrator
│   └── registry.py            → Skill registry
├── memory/
│   └── student_memory.py      → In-memory student state
├── evaluation/
│   ├── evaluation_engine.py   → Central evaluation processor
│   ├── confidence.py          → Confidence calculator
│   ├── readiness.py           → Readiness calculator
│   └── progress.py            → Progress calculator
├── services/
│   ├── ollama_service.py      → Ollama HTTP client
│   ├── memory_service.py      → DB ↔ memory sync
│   └── recommendation_service.py → Career recommendations
├── skills/
│   ├── survey/                → Career discovery skill
│   ├── assessment/            → Technical assessment skill
│   ├── learning/              → Roadmap generation skill
│   ├── interview/             → Mock interview skill
│   └── reflection/            → Self-reflection skill
├── auth/                      → JWT + password handlers
├── prompts/                   → System prompt markdown files
└── utils/                     → Shared utilities
```
