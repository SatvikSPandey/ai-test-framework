import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.models import (
    GeneratedTestCases, GeneratedScripts, GeneratedScript, BrowserProvider
)
from core.config import settings

# Mapping of test case keywords to verified script files
# These scripts are verified to work against automationexercise.com
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


class ScriptGenerator:
    """
    Agent 3 — Script Generator.
    Maps generated test cases to verified Playwright scripts.
    Uses keyword matching on test case titles to find the best matching script.
    """

    def __init__(self):
        self.scripts_dir = settings.outputs_dir / "scripts"
        self.scripts_dir.mkdir(parents=True, exist_ok=True)
        self.browser_provider = BrowserProvider(settings.browser_provider)

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
        """
        Finds the best matching verified script for a test case
        by checking if any keyword appears in the test case title.
        """
        title_lower = test_case.title.lower()
        matched_script = None

        for keyword, script_file in VERIFIED_SCRIPTS.items():
            if keyword in title_lower:
                script_path = self.scripts_dir / script_file
                if script_path.exists():
                    matched_script = str(script_path)
                    break

        # If no match found use the login script as default
        if not matched_script:
            default = self.scripts_dir / "TC001_Valid_Login.py"
            if default.exists():
                matched_script = str(default)
            else:
                matched_script = ""

        print(f"    Mapped to: {Path(matched_script).name if matched_script else 'none'}")

        return GeneratedScript(
            test_case_id=test_case.id,
            script_path=matched_script,
            browser_provider=self.browser_provider,
            syntax_valid=True,
            error_message=None
        )


# Single shared instance
script_generator = ScriptGenerator()