# Interview Skill Examples

**Example 1: Starting the interview**
User context: Target company: Google. Role: Frontend Engineer.
Output:
{
  "next_question": "Welcome! To start, could you tell me about a time you had to optimize a complex React application to improve its rendering performance?",
  "feedback": {"strengths": "", "improvements": ""},
  "overall_score": 0,
  "is_complete": false
}

**Example 2: Evaluating an answer**
User context: Answered "I used React.memo and useCallback to prevent unnecessary re-renders in a large list component."
Output:
{
  "next_question": "Good approach. Now, how would you handle a situation where state needs to be shared across many deeply nested components?",
  "feedback": {
    "strengths": "Clearly mentioned specific tools (React.memo, useCallback) and the problem they solved.",
    "improvements": "Could have used the STAR method to describe the specific situation and exact impact on load times."
  },
  "overall_score": 75,
  "is_complete": false
}
