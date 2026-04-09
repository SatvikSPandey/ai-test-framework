import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from playwright.sync_api import sync_playwright, Page, Browser
from core.config import settings


class PlaywrightRunner:
    """
    Playwright browser runner.
    Handles opening, controlling, and closing a Chromium browser.
    Used by Agent 4 (Test Executor) as an alternative to Selenium.
    Switch between them by changing browser_provider in config.py.
    """

    def __init__(self):
        self.playwright = None
        self.browser: Browser = None
        self.page: Page = None

    def start(self):
        """Opens a Chromium browser instance using Playwright."""
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(
            headless=settings.headless
        )
        self.page = self.browser.new_page()
        self.page.set_default_timeout(settings.browser_timeout * 1000)
        print("  Playwright Chromium browser started")

    def stop(self):
        """Closes the browser and cleans up."""
        if self.browser:
            self.browser.close()
        if self.playwright:
            self.playwright.stop()
        print("  Playwright browser closed")

    def navigate(self, url: str):
        """Navigates to a URL."""
        self.page.goto(url)

    def click(self, selector: str):
        """Finds an element by CSS selector and clicks it."""
        self.page.locator(selector).click()

    def type_text(self, selector: str, text: str):
        """Finds an input and types text into it."""
        self.page.locator(selector).fill(text)

    def get_text(self, selector: str) -> str:
        """Returns visible text of an element."""
        return self.page.locator(selector).inner_text()

    def take_screenshot(self, path: str):
        """Saves a screenshot of the current browser state to a file."""
        if self.page:
            self.page.screenshot(path=path)

    def run_script_file(self, script_path: str) -> tuple[bool, str | None]:
        """
        Executes a generated Python test script file as a subprocess.
        Returns (True, None) if the script prints PASSED.
        Returns (False, error_message) if it prints FAILED or crashes.
        """
        import subprocess

        try:
            result = subprocess.run(
                [sys.executable, script_path],
                capture_output=True,
                text=True,
                timeout=settings.browser_timeout * 2
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