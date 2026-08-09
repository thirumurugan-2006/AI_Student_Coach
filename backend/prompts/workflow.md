# AI Career Coach — System Workflow

## Full Request Lifecycle

```
1. User sends HTTP request to FastAPI endpoint
   └─ e.g. POST /survey/ {"user_message": "I want to become a backend engineer"}

2. FastAPI validates JWT token → extracts student_id

3. API endpoint calls career_agent.handle_request(student_id, skill_name, context)

4. Career Coach checks Student Memory
   └─ If student not found → creates default profile

5. Career Coach calls registry.execute(skill_name, context, schema)

6. Skill Registry instantiates/retrieves the correct skill instance

7. Skill loads instruction.md + examples.md (loaded at startup)

8. Skill reads Student Memory via get_profile_summary()

9. Skill builds prompt:
   [System Instructions] + [Student Profile] + [Skill Instructions] + [Examples] + [Context]

10. Skill calls LLM Interface → Ollama Service → llama3.2:3b

11. Ollama returns response (text or JSON)

12. LLM Interface validates JSON against Pydantic schema

13. Skill returns validated result to Career Coach

14. Career Coach sends result to Evaluation Engine

15. Evaluation Engine:
    └─ Updates knowledge graph (assessment)
    └─ Updates skills/confidence (interview, reflection)
    └─ Updates roadmap (learning)
    └─ Updates career goal (survey)
    └─ Recalculates readiness score
    └─ Updates Student Memory

16. Career Coach returns final result to API layer

17. API layer serialises result → JSON response to frontend
```

## Skill-Specific Workflows

### Survey Workflow
```
User answers career questions
→ SurveySkill builds profile extraction prompt
→ LLM returns StudentProfile + SurveyOutput JSON
→ Evaluation Engine updates career_goal, target_company, experience_level
→ survey_completed = True
→ Career Coach triggers Learning skill automatically (next session)
```

### Assessment Workflow
```
User selects topic to be assessed
→ AssessmentSkill generates adaptive question based on weak_topics
→ User answers
→ Next call: skill evaluates answer, generates next question
→ Evaluation Engine updates knowledge_graph, weak_topics, strong_topics
→ assessment_completed = True when is_complete = True
```

### Learning Workflow
```
User requests learning roadmap for a topic
→ LearningSkill generates resource list + project ideas + study schedule
→ Evaluation Engine updates roadmap
→ Student follows roadmap; marks topics complete via separate API calls
```

### Interview Workflow
```
User initiates mock interview with company + role
→ InterviewSkill generates first recruiter question
→ User answers → skill evaluates → generates next question
→ Evaluation Engine updates interview_history, confidence
→ Session ends when is_complete = True
```

### Reflection Workflow
```
User submits weekly reflection
→ ReflectionSkill analyses sentiment + confidence
→ Returns confidence_level, reflection_notes, suggested_action
→ Evaluation Engine updates confidence, adds to reflection_notes
```

## State Transitions

```
New User
   ↓
Survey → profile_complete
   ↓
Assessment → skills_mapped
   ↓
Learning → roadmap_active
   ↓
Interview → interview_ready
   ↓
Reflection (weekly) → continuous improvement
   ↓
Job Ready (readiness_score > 75)
```
