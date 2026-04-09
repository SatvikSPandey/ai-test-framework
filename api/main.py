import sys
from pathlib import Path

# Add project root to path so all imports work
sys.path.insert(0, str(Path(__file__).parent.parent))

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional

from agents.requirements_parser import requirements_parser
from agents.test_case_generator import test_case_generator
from agents.script_generator import script_generator
from agents.test_executor import test_executor
from agents.report_generator import ReportGenerator
from core.config import settings
from core.models import FinalReport

app = FastAPI(
    title="AI Test Automation Framework",
    description="Upload a requirements document and get automated test results back.",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)


# ── Request / Response Models ─────────────────────────────────────────────────

class TextRunRequest(BaseModel):
    """Request body for running the pipeline with plain text input."""
    text: str
    target_url: Optional[str] = None
    browser_provider: Optional[str] = "selenium"
    llm_provider: Optional[str] = "ollama"


class RunSummary(BaseModel):
    """Simplified response returned after a pipeline run."""
    run_id: str
    total_features: int
    total_test_cases: int
    total_passed: int
    total_failed: int
    coverage_percentage: float
    html_report_path: str
    excel_report_path: str
    json_report_path: str


# ── Routes ────────────────────────────────────────────────────────────────────

@app.get("/")
def root():
    """Health check endpoint."""
    return {
        "status": "running",
        "service": "AI Test Automation Framework",
        "version": "1.0.0"
    }


@app.get("/health")
def health():
    """Detailed health check."""
    return {
        "status": "healthy",
        "llm_provider": settings.llm_provider,
        "browser_provider": settings.browser_provider,
        "target_url": settings.target_url
    }


@app.post("/run/file", response_model=RunSummary)
async def run_from_file(file: UploadFile = File(...)):
    """
    Upload a PDF, DOCX, or TXT requirements document.
    Runs the full five-agent pipeline and returns a summary.
    """
    # Validate file type
    allowed_extensions = [".pdf", ".docx", ".txt"]
    file_ext = Path(file.filename).suffix.lower()

    if file_ext not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type: {file_ext}. Use PDF, DOCX, or TXT."
        )

    # Save uploaded file temporarily
    temp_path = settings.outputs_dir / file.filename
    content = await file.read()
    temp_path.write_bytes(content)

    try:
        return _run_pipeline(file_path=str(temp_path))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/run/text", response_model=RunSummary)
def run_from_text(request: TextRunRequest):
    """
    Send requirements as plain text in the request body.
    Runs the full five-agent pipeline and returns a summary.
    """
    # Apply optional overrides from request
    if request.target_url:
        settings.target_url = request.target_url
    if request.browser_provider:
        settings.browser_provider = request.browser_provider
    if request.llm_provider:
        settings.llm_provider = request.llm_provider

    try:
        return _run_pipeline(text=request.text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/reports")
def list_reports():
    """Lists all past report runs from the outputs directory."""
    outputs_dir = settings.outputs_dir
    run_folders = sorted(
        [f.name for f in outputs_dir.iterdir()
         if f.is_dir() and f.name.startswith("run_")],
        reverse=True
    )
    return {"runs": run_folders, "total": len(run_folders)}


# ── Pipeline Runner ───────────────────────────────────────────────────────────

def _run_pipeline(
    file_path: str = None,
    text: str = None
) -> RunSummary:
    """
    Internal function that runs all five agents in sequence.
    Called by both /run/file and /run/text endpoints.
    """
    # Agent 1 — Parse requirements
    print("Agent 1: Parsing requirements...")
    if file_path:
        parsed_requirements = requirements_parser.parse_file(file_path)
    else:
        parsed_requirements = requirements_parser.parse_text(text)

    # Agent 2 — Generate test cases
    print("Agent 2: Generating test cases...")
    generated_test_cases = test_case_generator.generate(parsed_requirements)

    # Agent 3 — Generate scripts
    print("Agent 3: Generating scripts...")
    generated_scripts = script_generator.generate(generated_test_cases)

    # Agent 4 — Execute tests
    print("Agent 4: Executing tests...")
    execution_results = test_executor.execute(generated_scripts)

    # Agent 5 — Generate report
    print("Agent 5: Generating report...")
    rg = ReportGenerator()
    final_report = rg.generate(
        parsed_requirements,
        generated_test_cases,
        generated_scripts,
        execution_results
    )

    return RunSummary(
        run_id=final_report.run_id,
        total_features=final_report.total_features,
        total_test_cases=final_report.total_test_cases,
        total_passed=final_report.total_passed,
        total_failed=final_report.total_failed,
        coverage_percentage=final_report.coverage_percentage,
        html_report_path=final_report.html_report_path,
        excel_report_path=final_report.excel_report_path,
        json_report_path=final_report.json_report_path
    )