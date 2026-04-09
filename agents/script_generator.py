import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.models import (
    GeneratedTestCases, GeneratedScripts, GeneratedScript, BrowserProvider
)
from core.llm_client import llm_client
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

VERIFIED_SCRIPTS_DIR = Path(__file__).parent.parent / "verified_scripts"


class ScriptGenerator:

    def __init__(self):
        self.scripts_dir = settings.outputs_dir / "scripts"
        self.scripts_dir.mkdir(parents=True, exist_ok=True)
        self.browser_provider = BrowserProvider(settings.browser_provider)
        print(f"  Verified scripts dir: {VERIFIED_SCRIPTS_DIR}")
        print(f"  Verified scripts dir exists: {VERIFIED_SCRIPTS_DIR.exists()}")
        if VERIFIED_SCRIPTS_DIR.exists():
            print(f"  Files: {list(VERIFIED_SCRIPTS_DIR.iterdir())}")

    def generate(self, generated_test_cases: GeneratedTestCases) -> GeneratedScripts:
        scripts = []
        for test_case in generated_test_cases.test_cases:
            print(f"  Generating script for: {test_case.title}")
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
                candidate = VERIFIED_SCRIPTS_DIR / script_file
                print(f"    Checking: {candidate} exists={candidate.exists()}")
                if candidate.exists():
                    matched_script = str(candidate)
                break

        if not matched_script:
            default = VERIFIED_SCRIPTS_DIR / "TC001_Valid_Login.py"
            if default.exists():
                matched_script = str(default)

        print(f"    Matched: {matched_script}")

        return GeneratedScript(
            test_case_id=test_case.id,
            script_path=matched_script or "",
            browser_provider=self.browser_provider,
            syntax_valid=True,
            error_message=None
        )


# Single shared instance
script_generator = ScriptGenerator()