import streamlit as st
import sys
import json
import subprocess
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

# Install Playwright browsers on Streamlit Cloud if not already installed
try:
    subprocess.run(
        [sys.executable, "-m", "playwright", "install", "chromium"],
        check=False,
        capture_output=True
    )
except Exception:
    pass

from agents.requirements_parser import requirements_parser
from agents.test_case_generator import test_case_generator
from agents.script_generator import script_generator
from agents.test_executor import test_executor
from agents.report_generator import ReportGenerator
from core.config import settings

st.set_page_config(
    page_title="AI Test Framework",
    page_icon="🤖",
    layout="wide"
)

# ── Session State Initialisation ──────────────────────────────────────────────
if "parsed_requirements" not in st.session_state:
    st.session_state.parsed_requirements = None
if "final_report" not in st.session_state:
    st.session_state.final_report = None
if "execution_results" not in st.session_state:
    st.session_state.execution_results = None

st.title("🤖 AI-Powered Test Automation Framework")
st.caption("Upload a requirements document and let the AI generate, execute, and report test cases automatically.")

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.header("⚙️ Configuration")

    target_url = st.text_input(
        "Target URL",
        value=settings.target_url,
        help="The website to run tests against"
    )

    browser_provider = st.selectbox(
        "Browser",
        options=["selenium", "playwright"],
        index=0
    )

    headless = st.checkbox("Run headless", value=True)

    confidence_threshold = st.slider(
        "Confidence threshold",
        min_value=0.0,
        max_value=1.0,
        value=settings.confidence_threshold,
        step=0.05,
        help="Test cases below this confidence score are skipped"
    )

    llm_provider = st.selectbox(
        "LLM Provider",
        options=["ollama", "cohere"],
        index=0
    )

    st.divider()
    st.caption("Settings apply to the current run only.")

# ── Main Area ─────────────────────────────────────────────────────────────────
tab1, tab2 = st.tabs(["📄 Run Tests", "📊 Past Reports"])

with tab1:
    st.subheader("Step 1 — Provide Requirements")

    input_method = st.radio(
        "Input method",
        options=["Upload a file", "Paste text"],
        horizontal=True
    )

    if input_method == "Upload a file":
        uploaded_file = st.file_uploader(
            "Upload requirements document",
            type=["pdf", "docx", "txt"],
            help="PDF, DOCX, or plain text files are supported"
        )

        if uploaded_file:
            temp_path = settings.outputs_dir / uploaded_file.name
            temp_path.write_bytes(uploaded_file.read())
            with st.spinner("Parsing requirements..."):
                try:
                    st.session_state.parsed_requirements = requirements_parser.parse_file(str(temp_path))
                    st.success(f"✅ Found {st.session_state.parsed_requirements.total_features} features")
                except Exception as e:
                    st.error(f"❌ Failed to parse file: {e}")

    else:
        pasted_text = st.text_area(
            "Paste your requirements or user story here",
            height=200,
            placeholder="Example:\nFeature: User Login\n..."
        )

        if st.button("Parse Requirements", type="primary"):
            if pasted_text.strip():
                with st.spinner("Parsing requirements..."):
                    try:
                        st.session_state.parsed_requirements = requirements_parser.parse_text(pasted_text)
                        st.success(f"✅ Found {st.session_state.parsed_requirements.total_features} features")
                    except Exception as e:
                        st.error(f"❌ Failed to parse text: {e}")
            else:
                st.warning("Please paste some requirements text first.")

    # Show parsed features if available in session state
    if st.session_state.parsed_requirements:
        with st.expander("📋 Parsed Features", expanded=False):
            for feature in st.session_state.parsed_requirements.features:
                st.markdown(f"**{feature.id} — {feature.name}**")
                st.caption(feature.description)
                for ac in feature.acceptance_criteria:
                    st.markdown(f"  - {ac.id}: {ac.description}")

        st.divider()
        st.subheader("Step 2 — Run the Pipeline")

        if st.button("🚀 Generate & Execute Tests", type="primary"):
            settings.target_url = target_url
            settings.browser_provider = browser_provider
            settings.headless = headless
            settings.confidence_threshold = confidence_threshold
            settings.llm_provider = llm_provider

            progress = st.progress(0)
            status = st.empty()

            try:
                # Agent 2
                status.info("🧠 Agent 2: Generating test cases...")
                progress.progress(20)
                generated_test_cases = test_case_generator.generate(
                    st.session_state.parsed_requirements
                )
                st.success(f"✅ Generated {generated_test_cases.total_test_cases} test cases")

                # Agent 3
                status.info("✍️ Agent 3: Writing test scripts...")
                progress.progress(40)
                generated_scripts = script_generator.generate(generated_test_cases)
                valid = sum(1 for s in generated_scripts.scripts if s.syntax_valid)
                st.success(f"✅ Generated {generated_scripts.total_scripts} scripts ({valid} valid)")

                # Agent 4
                status.info("▶️ Agent 4: Executing tests...")
                progress.progress(60)
                execution_results = test_executor.execute(generated_scripts)
                st.session_state.execution_results = execution_results
                st.success(f"✅ Executed {execution_results.total_tests} tests — {execution_results.passed} passed, {execution_results.failed} failed")

                # Agent 5
                status.info("📊 Agent 5: Generating reports...")
                progress.progress(80)
                rg = ReportGenerator()
                final_report = rg.generate(
                    st.session_state.parsed_requirements,
                    generated_test_cases,
                    generated_scripts,
                    execution_results
                )
                st.session_state.final_report = final_report
                progress.progress(100)
                status.success("✅ Pipeline complete!")

            except Exception as e:
                status.error(f"❌ Pipeline failed: {e}")
                st.exception(e)

    # Show results if pipeline has been run
    if st.session_state.final_report:
        report = st.session_state.final_report
        st.divider()
        st.subheader("📊 Results")

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total Tests", report.total_test_cases)
        col2.metric("Passed", report.total_passed)
        col3.metric("Failed", report.total_failed)
        col4.metric("Coverage", f"{report.coverage_percentage}%")

        st.subheader("📋 Coverage Map")
        for item in report.coverage_map:
            icon = "✅" if item.covered else "❌"
            st.markdown(f"{icon} **{item.feature_name}** — {item.tests_passed}/{item.tests_written} tests passing")

        st.divider()
        st.subheader("⬇️ Download Reports")

        col1, col2, col3 = st.columns(3)

        with col1:
            html_content = Path(report.html_report_path).read_text(encoding="utf-8")
            st.download_button(
                "📄 Download HTML Report",
                data=html_content,
                file_name="test_report.html",
                mime="text/html"
            )

        with col2:
            excel_bytes = Path(report.excel_report_path).read_bytes()
            st.download_button(
                "📊 Download Excel Report",
                data=excel_bytes,
                file_name="test_report.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

        with col3:
            json_content = Path(report.json_report_path).read_text(encoding="utf-8")
            st.download_button(
                "🔧 Download JSON Report",
                data=json_content,
                file_name="test_report.json",
                mime="application/json"
            )

with tab2:
    st.subheader("Past Reports")
    outputs_dir = settings.outputs_dir

    run_folders = sorted(
        [f for f in outputs_dir.iterdir() if f.is_dir() and f.name.startswith("run_")],
        reverse=True
    )

    if not run_folders:
        st.info("No past reports found. Run the pipeline first.")
    else:
        for folder in run_folders:
            json_files = list(folder.glob("*.json"))
            if json_files:
                with st.expander(f"📁 {folder.name}"):
                    data = json.loads(json_files[0].read_text(encoding="utf-8"))
                    col1, col2, col3 = st.columns(3)
                    col1.metric("Passed", data["summary"]["passed"])
                    col2.metric("Failed", data["summary"]["failed"])
                    col3.metric("Coverage", f"{data['summary']['coverage_percentage']}%")