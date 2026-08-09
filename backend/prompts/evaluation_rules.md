# AI Career Coach — Evaluation Rules

The Evaluation Engine (`evaluation/evaluation_engine.py`) is the
**only** component that processes skill results and updates student metrics.

---

## Core Principle

> No skill may compute a score. No API may update memory directly.
> All skill results flow through the Evaluation Engine.

---

## What the Evaluation Engine Does

For every skill execution, the Evaluation Engine:

1. Receives the raw result from the skill
2. Routes processing to the skill-specific handler
3. Updates the relevant memory fields
4. Recalculates all metrics (readiness, confidence, progress)
5. Writes updated state back to Student Memory

---

## Readiness Score Formula

```
readiness_score = (
    average_skill_score  * 0.40 +   # Technical skills (40%)
    average_interview_score * 0.30 + # Interview performance (30%)
    confidence_score * 0.20 +        # Self-assessed confidence (20%)
    roadmap_completion_pct * 0.10    # Roadmap completion (10%)
)
```

Score range: 0–100

| Score | Status |
|-------|--------|
| 75–100 | Job Ready |
| 50–74 | Progressing |
| 25–49 | Needs Work |
| 0–24 | Just Starting |

---

## Confidence Score Rules

- Default starting confidence: 50
- Updated after interview: `new = (current * 0.7) + (interview_score * 0.3)`
- Updated from reflection: set directly from `confidence_score` field
- Range: 0–100

---

## Knowledge Graph Status Values

```
"mastered"          → Concept fully understood
"proficient"        → Strong grasp, minor gaps
"learning"          → Currently studying
"needs_improvement" → Below proficiency
"not_started"       → Not yet covered
```

---

## Evaluation Processing By Skill

### Survey
- Updates: `career_goal`, `target_company`, `experience_level`, `learning_style`
- Sets: `survey_completed = True`

### Assessment
- Updates: `knowledge_graph` (topic → concept → status)
- Populates: `weak_topics`, `strong_topics`
- Triggers: readiness recalculation

### Learning
- Updates: `roadmap`
- Updates: `completed_topics` (if user marks topics done)

### Interview
- Appends to: `interview_history`
- Updates: `confidence` (from overall_score)
- Updates: `recruiter_feedback`

### Reflection
- Appends to: `reflection_notes`
- Updates: `confidence` (from confidence_score)

---

## Adding a New Evaluation Metric

1. Add the calculation logic to the appropriate calculator class (`confidence.py`, `readiness.py`, or `progress.py`)
2. Add a new `_process_<skill>()` method in `EvaluationEngine`
3. Call it from `EvaluationEngine.process()` in the skill routing block
4. Update `_recalculate_metrics()` if the metric affects overall readiness
5. Update this document
