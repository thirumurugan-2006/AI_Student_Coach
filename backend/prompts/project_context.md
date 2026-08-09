# AI Career Coach — Project Context

## What This System Is

The AI Career Coach is a personalized, AI-native career preparation platform built for students and junior engineers who want to break into the software industry.

The system uses a local Ollama LLM (llama3.2:3b) to power intelligent, context-aware coaching across five domains: career profiling, technical assessment, learning roadmap generation, mock interview simulation, and self-reflection.

## Core Value Proposition

- Personalized coaching that adapts to each student's background, goals, and learning pace
- Privacy-first: all AI processing runs locally via Ollama — no data leaves the machine
- Memory-driven: the system maintains a persistent understanding of each student across all sessions
- Modular architecture: each coaching domain is an isolated skill that can be improved independently

## Target Users

- Computer science students (final year or recent graduates)
- Junior software engineers (0–2 years experience)
- Career changers transitioning into software engineering

## System Scope

The backend provides the AI intelligence layer. A separate frontend handles the UI. The backend exposes a REST API that the frontend consumes.

## Technology Stack

| Layer | Technology |
|-------|-----------|
| Backend Framework | FastAPI (Python 3.11+) |
| LLM | Ollama — llama3.2:3b (local) |
| Database | SQLite (dev) / PostgreSQL (prod) |
| ORM | SQLAlchemy (async) |
| Auth | JWT (python-jose) |
| Memory | In-memory + DB persistence |

## Business Rules

1. The Career Coach is the single orchestrator — skills never control workflow
2. All LLM calls go through the LLM Interface (never call Ollama directly from skills)
3. All evaluations go through the Evaluation Engine (skills never calculate scores)
4. Student memory is the single source of truth for all student state
5. The backend must remain runnable even when Ollama is offline (graceful degradation)
