# Assessment Skill Examples

**Example 1: Generating the first question**
User context: Target role is Junior Backend Developer. Topic is 'Python'. No previous answer.
Output:
{
  "next_question": "Can you explain how a decorator works in Python and give an example of when you would use one?",
  "difficulty": "medium",
  "feedback": "Let's start our assessment on Python.",
  "topic_evaluations": {},
  "is_complete": false
}

**Example 2: Evaluating an answer**
User context: Answered "A decorator takes a function and adds functionality without modifying it. I'd use it for logging."
Output:
{
  "next_question": "Great! Now, how would you handle passing arguments to a decorator itself?",
  "difficulty": "hard",
  "feedback": "Excellent answer! You accurately described the wrapper pattern.",
  "topic_evaluations": {
    "Python": {
      "Decorators": "mastered"
    }
  },
  "is_complete": false
}
