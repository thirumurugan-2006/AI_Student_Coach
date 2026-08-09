"""
Coding Evaluator

Evaluates coding submissions using test cases.
"""

from typing import Dict, Any
import subprocess
import tempfile
import os


class CodingEvaluator:
    """
    Evaluates code submissions against test cases.
    """

    async def evaluate(self, submission: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluate a code submission.

        Args:
            submission: Dictionary containing code, language, and test_cases

        Returns:
            Evaluation result with score and feedback
        """
        code = submission.get("code", "")
        language = submission.get("language", "python")
        test_cases = submission.get("test_cases", [])

        if not code or not test_cases:
            return {
                "score": 0.0,
                "passed": 0,
                "total": len(test_cases),
                "feedback": "No code or test cases provided"
            }

        passed = 0
        results = []

        for i, test_case in enumerate(test_cases):
            try:
                result = await self._run_test_case(code, language, test_case)
                results.append(result)
                if result.get("passed", False):
                    passed += 1
            except Exception as e:
                results.append({"passed": False, "error": str(e)})

        total = len(test_cases)
        score = (passed / total * 100) if total > 0 else 0.0

        return {
            "score": round(score, 2),
            "passed": passed,
            "total": total,
            "results": results,
            "feedback": f"Passed {passed}/{total} test cases"
        }

    async def _run_test_case(self, code: str, language: str, test_case: Dict[str, Any]) -> Dict[str, Any]:
        """
        Run a single test case against the code.
        """
        if language.lower() != "python":
            return {"passed": False, "error": f"Language {language} not supported yet"}

        input_data = test_case.get("input", "")
        expected_output = test_case.get("expected_output", "")

        try:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                f.write(code)
                f.write(f"\nprint({input_data})")
                temp_file = f.name

            result = subprocess.run(
                ["python", temp_file],
                capture_output=True,
                text=True,
                timeout=10
            )

            actual_output = result.stdout.strip()
            passed = actual_output == expected_output.strip()

            return {
                "passed": passed,
                "expected": expected_output,
                "actual": actual_output
            }
        except subprocess.TimeoutExpired:
            return {"passed": False, "error": "Timeout"}
        except Exception as e:
            return {"passed": False, "error": str(e)}
        finally:
            if 'temp_file' in locals() and os.path.exists(temp_file):
                os.unlink(temp_file)
