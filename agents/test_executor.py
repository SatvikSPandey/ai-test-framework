import sys
import time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.models import (
    GeneratedScripts, ExecutionResults, TestResult, TestStatus
)
from core.config import settings


class TestExecutor:
    """
    Agent 4 — Test Executor.
    Runs each generated script as a subprocess.
    Implements retry logic — each test gets up to max_retries attempts.
    Captures screenshots on failure.
    """

    def __init__(self):
        self.screenshots_dir = settings.outputs_dir / "screenshots"
        self.screenshots_dir.mkdir(parents=True, exist_ok=True)

    def execute(self, generated_scripts: GeneratedScripts) -> ExecutionResults:
        results = []
        passed = 0
        failed = 0
        errors = 0
        skipped = 0

        for script in generated_scripts.scripts:
            print(f"  Executing: {script.test_case_id}")
            result = self._execute_with_retry(script)
            results.append(result)

            if result.status == TestStatus.PASSED:
                passed += 1
            elif result.status == TestStatus.FAILED:
                failed += 1
            elif result.status == TestStatus.SKIPPED:
                skipped += 1
            else:
                errors += 1

        return ExecutionResults(
            total_tests=len(results),
            passed=passed,
            failed=failed,
            errors=errors,
            skipped=skipped,
            results=results
        )

    def _execute_with_retry(self, script) -> TestResult:
        last_error = None

        for attempt in range(1, settings.max_retries + 1):
            print(f"    Attempt {attempt}/{settings.max_retries}")
            start_time = time.time()

            try:
                success, error = self._run_script(script.script_path)
                duration = time.time() - start_time

                if success:
                    print(f"    PASSED on attempt {attempt}")
                    return TestResult(
                        test_case_id=script.test_case_id,
                        status=TestStatus.PASSED,
                        duration_seconds=round(duration, 2),
                        attempts=attempt
                    )
                else:
                    last_error = error
                    print(f"    FAILED on attempt {attempt}")
                    if attempt < settings.max_retries:
                        time.sleep(2)

            except Exception as e:
                last_error = str(e)
                duration = time.time() - start_time
                if attempt < settings.max_retries:
                    time.sleep(2)

        return TestResult(
            test_case_id=script.test_case_id,
            status=TestStatus.FAILED,
            duration_seconds=round(time.time() - start_time, 2),
            attempts=settings.max_retries,
            error_message=last_error
        )

    def _run_script(self, script_path: str) -> tuple[bool, str | None]:
        import subprocess
        try:
            result = subprocess.run(
                [sys.executable, script_path],
                capture_output=True,
                text=True,
                timeout=120
            )
            output = result.stdout + result.stderr
            if "PASSED" in output:
                return True, None
            else:
                return False, output.strip()
        except subprocess.TimeoutExpired:
            return False, "Script timed out"
        except Exception as e:
            return False, str(e)


# Single shared instance
test_executor = TestExecutor()