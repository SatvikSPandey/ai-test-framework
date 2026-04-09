from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum

# ─── Enums ───────────────────────────────────────────────────────────────────

class Priority(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

class TestStatus(str, Enum):
    PASSED = "passed"
    FAILED = "failed"
    ERROR = "error"
    SKIPPED = "skipped"

class BrowserProvider(str, Enum):
    SELENIUM = "selenium"
    PLAYWRIGHT = "playwright"

# ─── Agent 1 Output: Requirements Parser ─────────────────────────────────────

class AcceptanceCriteria(BaseModel):
    id: str
    description: str

class Feature(BaseModel):
    id: str
    name: str
    description: str
    acceptance_criteria: list[AcceptanceCriteria]

class ParsedRequirements(BaseModel):
    source_file: str
    total_features: int
    features: list[Feature]

# ─── Agent 2 Output: Test Case Generator ─────────────────────────────────────

class TestStep(BaseModel):
    step_number: int
    action: str

class TestCase(BaseModel):
    id: str
    feature_id: str
    title: str
    priority: Priority
    preconditions: list[str]
    steps: list[TestStep]
    expected_result: str
    confidence_score: float = Field(ge=0.0, le=1.0)

class GeneratedTestCases(BaseModel):
    total_test_cases: int
    test_cases: list[TestCase]

# ─── Agent 3 Output: Script Generator ────────────────────────────────────────

class GeneratedScript(BaseModel):
    test_case_id: str
    script_path: str
    browser_provider: BrowserProvider
    syntax_valid: bool
    error_message: Optional[str] = None

class GeneratedScripts(BaseModel):
    total_scripts: int
    scripts: list[GeneratedScript]

# ─── Agent 4 Output: Test Executor ───────────────────────────────────────────

class TestResult(BaseModel):
    test_case_id: str
    status: TestStatus
    duration_seconds: float
    attempts: int
    screenshot_path: Optional[str] = None
    error_message: Optional[str] = None

class ExecutionResults(BaseModel):
    total_tests: int
    passed: int
    failed: int
    errors: int
    skipped: int
    results: list[TestResult]

# ─── Agent 5 Output: Report Generator ────────────────────────────────────────

class CoverageItem(BaseModel):
    feature_id: str
    feature_name: str
    total_criteria: int
    tests_written: int
    tests_passed: int
    covered: bool

class FinalReport(BaseModel):
    run_id: str
    target_url: str
    total_features: int
    total_test_cases: int
    total_passed: int
    total_failed: int
    coverage_percentage: float
    coverage_map: list[CoverageItem]
    html_report_path: str
    excel_report_path: str
    json_report_path: str