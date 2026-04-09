from playwright.sync_api import sync_playwright


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        try:
            page.goto("https://automationexercise.com/login")

            page.locator("input[data-qa='login-email']").fill("satvik_test_2026@gmail.com")
            page.locator("input[data-qa='login-password']").fill("Test@1234")
            page.locator("button[data-qa='login-button']").click()

            page.wait_for_url("https://automationexercise.com/", timeout=30000)
            print("PASSED")

        except Exception as e:
            print(f"FAILED: {e}")
        finally:
            browser.close()


if __name__ == "__main__":
    main()