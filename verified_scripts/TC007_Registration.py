from playwright.sync_api import sync_playwright
import random
import string


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        try:
            random_str = ''.join(random.choices(string.ascii_lowercase, k=6))
            email = f"test_{random_str}@testmail.com"

            page.goto("https://automationexercise.com/login")

            page.locator("input[data-qa='signup-name']").fill("Satvik P")
            page.locator("input[data-qa='signup-email']").fill(email)
            page.locator("button[data-qa='signup-button']").click()

            page.wait_for_url("https://automationexercise.com/signup", timeout=15000)

            page.locator("#id_gender1").check()
            page.locator("input[data-qa='password']").fill("Test@1234")

            page.locator("select[data-qa='days']").select_option("2")
            page.locator("select[data-qa='months']").select_option("7")
            page.locator("select[data-qa='years']").select_option("1997")

            page.locator("input[data-qa='first_name']").fill("Satvik")
            page.locator("input[data-qa='last_name']").fill("P")
            page.locator("input[data-qa='address']").fill("Somewhere in the World")
            page.locator("select[data-qa='country']").select_option("India")
            page.locator("input[data-qa='state']").fill("Gujarat")
            page.locator("input[data-qa='city']").fill("Vadodara")
            page.locator("input[data-qa='zipcode']").fill("390023")
            page.locator("input[data-qa='mobile_number']").fill("8357808521")

            page.locator("button[data-qa='create-account']").click()

            page.wait_for_url("https://automationexercise.com/account_created", timeout=15000)
            print("PASSED")

        except Exception as e:
            print(f"FAILED: {e}")
        finally:
            browser.close()


if __name__ == "__main__":
    main()