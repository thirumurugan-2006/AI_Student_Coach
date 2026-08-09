# AI Career Coach — Global Rules

These rules apply to ALL components across the entire system.
Every developer, code generator, and LLM working on this project must follow them.

---

## Architecture Rules

1. **The Career Coach is the sole orchestrator.**
   No skill, service, or utility may call another skill directly.
   All skill execution must go through `CareerCoach.handle_request()`.

2. **Skills never evaluate.**
   Skills return raw LLM output. The Evaluation Engine processes results.
   Skills must NOT calculate readiness scores, update confidence, or modify memory directly.

3. **LLM calls go through LLMInterface only.**
   Never import GroqService directly in a skill, API, or service.
   Always use `LLMInterface` for LLM calls.

4. **Student Memory is the single source of truth.**
   Never pass student data around as loose dictionaries between components.
   Always read from and write to `StudentMemory`.

5. **Repository Pattern for all database access.**
   No SQLAlchemy queries outside of repository classes.
   API endpoints, services, and skills must use repositories only.

---

## Code Quality Rules

6. **All functions must have type hints.**
   Python `Any` is only permitted when truly necessary.

7. **All public functions must have docstrings.**
   Minimum: one-line description + Args/Returns for non-trivial functions.

8. **Async all the way down.**
   All I/O operations (DB, HTTP, file) must use `async/await`.
   No blocking calls inside async functions.

9. **No hardcoded strings in business logic.**
   All skill names, score thresholds, and magic strings live in `core/constants.py`.

10. **Logging at every boundary.**
    Log when entering a skill, calling the LLM, processing evaluation results,
    and on all error paths.

---

## LLM Rules

11. **Only Groq is permitted.**
    OpenAI, Gemini, Claude, HuggingFace Inference APIs, and local Ollama are NEVER used.

12. **Always request JSON format when a schema is needed.**
    Set response_format to json_object in the Groq payload and validate with a Pydantic schema.

13. **Retry on failure.**
    All LLM calls use the RetryHandler decorator (max 3 retries, exponential backoff).

14. **Never expose raw LLM errors to the frontend.**
    Wrap LLM exceptions in `LLMException` and return a 503 status.

---

## Security Rules

15. **Never log passwords, tokens, or PII.**

16. **All authenticated endpoints must use `get_current_student_id` dependency.**
    Never trust user_id from the request body — always extract from JWT.

17. **SECRET_KEY must be changed before production deployment.**
    The default value in `.env.example` must never be used in production.

---

## Testing Rules

18. **Every new service must have at least one unit test.**

19. **Every new API endpoint must have at least one integration test.**

20. **Tests must not depend on a live Ollama server.**
    Use mocking for all LLM calls in tests.
