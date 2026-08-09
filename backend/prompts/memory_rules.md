# AI Career Coach — Memory Rules

These rules govern how Student Memory is used across the system.

---

## Memory Architecture

Student Memory operates on two levels:

1. **In-Memory Store** (`memory/student_memory.py`)
   - Fast dictionary-based store
   - Active during the request lifecycle
   - Updated by the Evaluation Engine after every skill execution

2. **Persistent Store** (SQLite / PostgreSQL via `services/memory_service.py`)
   - Written to disk after each session
   - Loaded back into memory on authentication
   - Source of truth across sessions

---

## Memory Read Rules

- Skills MUST read student context from `StudentMemory.get_profile(student_id)`
- Skills use `get_profile_summary()` to get a formatted string for LLM prompts
- API endpoints MUST NOT read raw database tables for student state — always use memory

---

## Memory Write Rules

- Skills NEVER write to memory directly
- Only the Evaluation Engine writes to memory (via `student_memory.*` methods)
- The MemoryPersistenceService flushes memory to DB after skill processing

---

## Memory Fields

| Field | Type | Description |
|-------|------|-------------|
| `career_goal` | str | Target career role |
| `target_company` | str | Dream company |
| `experience_level` | str | beginner/intermediate/advanced |
| `study_hours` | int | Daily study hours |
| `learning_style` | str | visual/reading/hands-on |
| `skills` | dict | `{skill_name: score_0_100}` |
| `knowledge_graph` | dict | `{topic: {concept: status}}` |
| `roadmap` | list | Ordered list of topics to study |
| `completed_topics` | list | Topics marked as completed |
| `weak_topics` | list | Topics needing improvement |
| `strong_topics` | list | Mastered topics |
| `assessment_history` | list | All assessment results |
| `interview_history` | list | All interview session results |
| `reflection_notes` | list | All reflection entries |
| `readiness_score` | float | 0–100 job-readiness score |
| `survey_completed` | bool | Survey completion flag |
| `assessment_completed` | bool | Assessment completion flag |
| `interview_completed` | bool | Interview completion flag |

---

## Memory Lifecycle

```
User logs in
   ↓
MemoryPersistenceService.load_from_db(db, user_id)
   ↓
StudentMemory populated with persisted data
   ↓
Request → Skill → Evaluation Engine → Memory updated
   ↓
MemoryPersistenceService.flush_to_db(db, user_id)
   ↓
Database updated
```

---

## Memory Isolation

Each student has their own isolated memory namespace keyed by `student_id`.
The in-memory `students` dictionary is scoped to the application lifetime.
On server restart, memory is re-populated from the database.
