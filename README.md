# 🤖 AI-Powered Test Automation Framework

An intelligent test automation framework that takes a requirements document as input and automatically generates, executes, and reports test cases using LLMs, Selenium, and Playwright.

Built as a freelance portfolio project demonstrating production-grade AI engineering combined with QA automation expertise.

---

## 🏗️ Architecture

The framework runs five AI agents in sequence:

Requirements Document
↓
[Agent 1] Requirements Parser    → Extracts features and acceptance criteria
↓
[Agent 2] Test Case Generator    → LLM generates BDD test cases with confidence scores
↓
[Agent 3] Script Generator       → LLM writes Selenium / Playwright Python scripts
↓
[Agent 4] Test Executor          → Runs scripts with retry logic and screenshot capture
↓
[Agent 5] Report Generator       → Produces HTML dashboard, Excel, and JSON reports

---

## ✨ Key Features

- **Multi-format input** — Upload PDF, DOCX, or TXT requirements documents, or paste text directly
- **BDD test case generation** — Given / When / Then format with confidence scoring
- **Dual browser support** — Selenium and Playwright behind a single abstraction layer
- **Retry logic** — Each test gets up to 3 attempts before marking as failed
- **Requirement coverage mapping** — Tracks which requirements have passing tests
- **Three report formats** — HTML dashboard, Excel (5 sheets), JSON
- **REST API** — FastAPI layer for CI/CD integration
- **Web UI** — Streamlit interface for non-technical users
- **Local LLM support** — Runs fully offline with Ollama (Llama 3, CodeLlama)

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Language | Python 3.13 |
| LLM (local) | Ollama — Llama 3, CodeLlama |
| LLM (cloud) | Cohere API |
| Browser automation | Selenium 4, Playwright |
| Web framework | FastAPI + Streamlit |
| Data validation | Pydantic v2 |
| Report generation | Jinja2, openpyxl |
| Containerisation | Docker + Docker Compose |

---

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Google Chrome
- [Ollama](https://ollama.ai) installed and running

### Installation

```bash
# Clone the repository
git clone https://github.com/SatvikSPandey/ai-test-framework.git
cd ai-test-framework

# Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Mac/Linux

# Install dependencies
pip install -r requirements.txt

# Install Playwright browsers
playwright install

# Pull the LLM model
ollama pull codellama
```

### Running the Framework

**Windows (recommended):**
```bash
.\start_framework.bat
```

**Manual:**
```bash
# Start Ollama in a separate terminal
ollama serve

# Launch Streamlit UI
streamlit run ui/app.py

# Or launch FastAPI
uvicorn api.main:app --reload
```

Open `http://localhost:8501` in your browser.

---

## 📖 Usage

1. Open the Streamlit UI at `http://localhost:8501`
2. Paste your requirements document or upload a PDF/DOCX/TXT file
3. Click **Parse Requirements** — the AI extracts features and acceptance criteria
4. Click **Generate & Execute Tests** — all 5 agents run automatically
5. Download the HTML, Excel, or JSON report

### Example Requirements Format

Feature: User Login
Registered users can log in to access their account.
Acceptance Criteria:

User can log in with valid email and password
Invalid credentials display an error message
Successful login redirects user to the home page

---

## 📊 Sample Output

- ✅ 10 test cases generated from 4 features
- ✅ 10/10 tests passing
- ✅ 100% requirement coverage
- ✅ HTML dashboard, Excel report (5 sheets), JSON report generated

---

## 🔌 REST API

Start the API server:
```bash
uvicorn api.main:app --reload
```

Interactive docs available at `http://localhost:8000/docs`

**Endpoints:**
- `GET /health` — Health check
- `POST /run/file` — Upload a requirements document and run the pipeline
- `POST /run/text` — Send requirements as plain text
- `GET /reports` — List all past report runs

---

## 🐳 Docker

```bash
docker-compose up --build
```

Services:
- Streamlit UI → `http://localhost:8501`
- FastAPI → `http://localhost:8000`
- Ollama → `http://localhost:11434`

---

## 📁 Project Structure

ai-test-framework/
├── agents/
│   ├── requirements_parser.py    # Agent 1 — document parsing
│   ├── test_case_generator.py    # Agent 2 — BDD test generation
│   ├── script_generator.py       # Agent 3 — script generation
│   ├── test_executor.py          # Agent 4 — test execution
│   └── report_generator.py      # Agent 5 — report generation
├── core/
│   ├── config.py                 # Central configuration
│   ├── llm_client.py             # Ollama / Cohere abstraction
│   └── models.py                 # Pydantic data models
├── runners/
│   ├── selenium_runner.py        # Selenium browser runner
│   └── playwright_runner.py      # Playwright browser runner
├── api/
│   └── main.py                   # FastAPI REST layer
├── ui/
│   └── app.py                    # Streamlit web interface
├── templates/
│   └── report.html               # Jinja2 HTML report template
├── sample_requirements/
│   └── sample_requirements.txt   # Example requirements document
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── start_framework.bat

---

## 👤 Author

**Satvik Pandey** — AI Engineer / Python Developer  
[LinkedIn](https://www.linkedin.com/in/satvik-pandey-433555365)

---

## 📄 License

MIT License
