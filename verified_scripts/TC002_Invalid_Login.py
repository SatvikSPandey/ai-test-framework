from playwright.sync_api import sync_playwright


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        try:
            page.goto("https://automationexercise.com/login")
            page.locator("input[data-qa='login-email']").fill("wrong@email.com")
            page.locator("input[data-qa='login-password']").fill("wrongpassword")
            page.locator("button[data-qa='login-button']").click()

            error = page.locator("p:has-text('Your email or password is incorrect')")
            error.wait_for(timeout=10000)
            print("PASSED")

        except Exception as e:
            print(f"FAILED: {e}")
        finally:
            browser.close()


if __name__ == "__main__":
    main()