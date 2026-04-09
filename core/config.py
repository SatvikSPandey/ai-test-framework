import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from pydantic_settings import BaseSettings
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent

class Settings(BaseSettings):
    # Project paths
    outputs_dir: Path = BASE_DIR / "outputs"
    templates_dir: Path = BASE_DIR / "templates"
    sample_requirements_dir: Path = BASE_DIR / "sample_requirements"

    # LLM settings
    llm_provider: str = "ollama"
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "codellama"
    cohere_api_key: str = ""
    cohere_model: str = "command-r-plus-08-2024"
    cohere_request_delay: float = 2.0

    # Browser settings
    browser_provider: str = "playwright"
    headless: bool = True
    browser_timeout: int = 30
    max_retries: int = 3

    # Target website
    target_url: str = "https://automationexercise.com"

    # Test settings
    confidence_threshold: float = 0.7
    max_test_cases_per_feature: int = 5

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()

# Ensure output directories exist
settings.outputs_dir.mkdir(parents=True, exist_ok=True)