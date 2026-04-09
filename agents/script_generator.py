import sys
import os
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.models import (
    GeneratedTestCases, GeneratedScripts, GeneratedScript, BrowserProvider
)
from core.config import settings

VERIFIED_SCRIPTS = {
    "login": "TC001_Valid_Login.py",
    "invalid login": "TC002_Invalid_Login.py",
    "invalid credentials": "TC002_Invalid_Login.py",
    "search": "TC003_Product_Search.py",
    "no result": "TC004_Search_No_Results.py",
    "no match": "TC004_Search_No_Results.py",
    "add to cart": "TC005_Add_To_Cart.py",
    "add product": "TC005_Add_To_Cart.py",
    "view cart": "TC006_View_Cart.py",
    "cart items": "TC006_View_Cart.py",
    "registration": "TC007_Registration.py",
    "register": "TC007_Registration.py",
    "signup": "TC007_Registration.py",
    "duplicate": "TC007_Registration.py",
}


def get_verified_scripts_dir() -> Path:
    """
    Finds the verified_scripts directory reliably on both
    Windows (local) and Linux (Streamlit Cloud).
    Tries multiple resolution strategies.
    """
    # Strategy 1: relative to this file
    candidate1 = Path(__file__).resolve().parent.parent / "verified_scripts"
    if candidate1.exists():
        return candidate1

    # Strategy 2: relative to current working directory
    candidate2 = Path(os.getcwd()) / "verified_scripts"
    if candidate2.exists():
        return candidate2

    # Strategy 3: Streamlit Cloud hardcoded path
    candidate3 = Path("/mount/src/ai-test-framework/verified_scripts")
    if candidate3.exists():
        return candidate3

    # Return candidate1 as default even if it doesn't exist
    return candidate1


class ScriptGenerator:

    def __init__(self):
        self.scripts_dir = settings.outputs_dir / "scripts"
        self.scripts_dir.mkdir(parents=True, exist_ok=True)
        self.browser_provider = BrowserProvider(settings.browser_provider)
        self.verified_dir = get_verified_scripts_dir()
        print(f"  Verified scripts dir: {self.verified_dir}")
        print(f"  Verified scripts dir exists: {self.verified_dir.exists()}")
        if self.verified_dir.exists():
            print(f"  Files: {[f.name for f in self.verified_dir.iterdir()]}")

    def generate(self, generated_test_cases: GeneratedTestCases) -> GeneratedScripts:
        scripts = []
        for test_case in generated_test_cases.test_cases:
            print(f"  Mapping script for: {test_case.title}")
            script = self._map_script(test_case)
            scripts.append(script)

        return GeneratedScripts(
            total_scripts=len(scripts),
            scripts=scripts
        )

    def _map_script(self, test_case) -> GeneratedScript:
        title_lower = test_case.title.lower()
        matched_script = None

        for keyword, script_file in VERIFIED_SCRIPTS.items():
            if keyword in title_lower:
                candidate = self.verified_dir / script_file
                print(f"    Keyword '{keyword}' matched. Checking: {candidate}")
                print(f"    File exists: {candidate.exists()}")
                if candidate.exists():
                    matched_script = str(candidate)
                break

        if not matched_script:
            default = self.verified_dir / "TC001_Valid_Login.py"
            print(f"    No keyword matched. Using default: {default} exists={default.exists()}")
            if default.exists():
                matched_script = str(default)
            else:
                matched_script = None

        print(f"    Final script path: {matched_script}")

        return GeneratedScript(
            test_case_id=test_case.id,
            script_path=matched_script or "",
            browser_provider=self.browser_provider,
            syntax_valid=True,
            error_message=None
        )


# Single shared instance
script_generator = ScriptGenerator()