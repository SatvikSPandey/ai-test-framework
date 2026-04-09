import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import subprocess
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from core.config import settings


class SeleniumRunner:

    def __init__(self):
        self.driver = None

    def start(self):
        options = Options()
        if settings.headless:
            options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--disable-gpu")
        # Selenium 4.6+ has built-in driver manager — no need for ChromeDriverManager
        self.driver = webdriver.Chrome(options=options)
        self.driver.set_page_load_timeout(settings.browser_timeout)
        print("  Selenium Chrome browser started")

    def stop(self):
        if self.driver:
            self.driver.quit()
            self.driver = None

    def navigate(self, url: str):
        self.driver.get(url)

    def find_element(self, by: str, value: str):
        wait = WebDriverWait(self.driver, settings.browser_timeout)
        by_map = {
            "css": By.CSS_SELECTOR,
            "xpath": By.XPATH,
            "id": By.ID,
            "name": By.NAME,
            "class": By.CLASS_NAME,
            "tag": By.TAG_NAME
        }
        by_type = by_map.get(by.lower(), By.CSS_SELECTOR)
        return wait.until(EC.presence_of_element_located((by_type, value)))

    def click(self, by: str, value: str):
        element = self.find_element(by, value)
        element.click()

    def type_text(self, by: str, value: str, text: str):
        element = self.find_element(by, value)
        element.clear()
        element.send_keys(text)

    def get_text(self, by: str, value: str) -> str:
        element = self.find_element(by, value)
        return element.text

    def take_screenshot(self, path: str):
        if self.driver:
            self.driver.save_screenshot(path)

    def run_script_file(self, script_path: str) -> tuple[bool, str | None]:
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


# Single shared instance
selenium_runner = SeleniumRunner()