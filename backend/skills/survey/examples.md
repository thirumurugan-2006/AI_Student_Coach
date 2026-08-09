# Survey Skill Examples

**Example 1: Initial survey question**
User context: No existing memory. First interaction.
Output:
{
  "status": "in_progress",
  "survey_completed": false,
  "profile": {
    "career_goal": "",
    "target_company": null,
    "experience_level": "",
    "primary_language": "",
    "known_skills": [],
    "projects": 0,
    "study_hours": 0,
    "learning_style": "",
    "weak_topics": [],
    "timeline": ""
  },
  "confidence": 0.0,
  "missing_information": ["career_goal", "experience_level", "primary_language", "learning_style", "timeline"],
  "coach_notification": "Starting survey. Need to collect basic career information."
}

**Example 2: After collecting career goal**
User context: Student wants to become an AI Engineer.
Output:
{
  "status": "in_progress",
  "survey_completed": false,
  "profile": {
    "career_goal": "AI Engineer",
    "target_company": null,
    "experience_level": "",
    "primary_language": "",
    "known_skills": [],
    "projects": 0,
    "study_hours": 0,
    "learning_style": "",
    "weak_topics": [],
    "timeline": ""
  },
  "confidence": 0.2,
  "missing_information": ["experience_level", "primary_language", "learning_style", "timeline"],
  "coach_notification": "Career goal collected. Now need to understand technical background."
}

**Example 3: Partial profile collected**
User context: Career goal: AI Engineer, Experience: Beginner, Language: Python, Study hours: 4, Learning style: Hands-on
Output:
{
  "status": "in_progress",
  "survey_completed": false,
  "profile": {
    "career_goal": "AI Engineer",
    "target_company": null,
    "experience_level": "Beginner",
    "primary_language": "Python",
    "known_skills": [],
    "projects": 0,
    "study_hours": 4,
    "learning_style": "Hands-on",
    "weak_topics": [],
    "timeline": ""
  },
  "confidence": 0.6,
  "missing_information": ["timeline"],
  "coach_notification": "Most information collected. Need placement timeline to complete profile."
}

**Example 4: Survey completed**
User context: All required fields collected including timeline: 6 months
Output:
{
  "status": "completed",
  "survey_completed": true,
  "profile": {
    "career_goal": "AI Engineer",
    "target_company": "Google",
    "experience_level": "Beginner",
    "primary_language": "Python",
    "known_skills": ["Python", "Basic ML"],
    "projects": 2,
    "study_hours": 4,
    "learning_style": "Hands-on",
    "weak_topics": ["Deep Learning", "Math"],
    "timeline": "6 months"
  },
  "confidence": 0.85,
  "missing_information": [],
  "coach_notification": "All required information collected. Profile is complete for personalized coaching."
}
