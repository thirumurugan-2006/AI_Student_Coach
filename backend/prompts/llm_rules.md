# AI Career Coach — LLM Rules

Rules for all interactions with the Ollama LLM service.

---

## Approved Models

| Model | Use Case |
|-------|----------|
| `llama3.2:3b` | Default — all skills, fast inference |

No other models, providers, or APIs are permitted in this system.

---

## Prompt Engineering Rules

### Structure
Every prompt sent to the LLM must follow this structure:

```
[System Role]
You are an AI Career Coach assistant. Your role is to <skill-specific role>.

[Student Profile]
{student_profile_summary}

[Skill Instructions]
{instruction.md content}

[Examples]
{examples.md content}

[Current Context]
{formatted context from the current request}

[Output Format]
Respond ONLY with valid JSON matching this schema:
{pydantic_schema_description}
```

### Tone
- Professional but encouraging
- Specific and actionable, never vague
- Never use filler phrases like "great question!" or "certainly!"
- Speak directly to the student as "you"

### JSON Output
- Always request JSON format when a Pydantic schema is expected
- Set `format: "json"` in the Ollama payload
- Never ask the LLM to wrap JSON in markdown code blocks

---

## Error Handling Rules

| Error | Action |
|-------|--------|
| Connection refused | Raise `LLMException`, return 503 |
| Timeout | Retry with backoff (max 3 attempts) |
| Invalid JSON | Retry with backoff; if all fail, raise `LLMException` |
| Schema validation failure | Retry with corrected prompt; if fail, raise `ValueError` |
| Empty response | Retry; if fail, raise `LLMException` |

---

## Performance Guidelines

- Keep prompts under 2,000 tokens for `llama3.2:3b`
- Set `num_predict: 2048` to cap token usage
- Set `temperature: 0.3` for consistent, structured output
- Set `top_p: 0.9` for controlled randomness
- Timeout: 120 seconds

---

## Retry Configuration

```python
@RetryHandler.with_retries(max_retries=3, base_delay=2.0, max_delay=10.0)
async def generate(...):
    ...
```

Exponential backoff: 2s → 4s → 8s (capped at 10s)

---

## Testing Rules

- All unit tests MUST mock `OllamaService.generate()`
- Never test against a live Ollama server in CI
- Use `unittest.mock.AsyncMock` for async method patching

---

## Monitoring

Log the following for every LLM call:
- Model name
- Prompt token estimate (character count / 4)
- Response time (ms)
- Success or failure status
- Retry attempt number (if applicable)
