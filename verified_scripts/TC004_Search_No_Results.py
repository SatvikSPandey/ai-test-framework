from playwright.sync_api import sync_playwright


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        try:
            page.goto("https://automationexercise.com/products")
            page.locator("#search_product").fill("xyzproductdoesnotexist123")
            page.locator("#submit_search").click()
            page.wait_for_timeout(3000)
            results = page.locator(".product-image-wrapper").count()
            if results == 0:
                print("PASSED")
            else:
                print("FAILED: Expected no results but found some")

        except Exception as e:
            print(f"FAILED: {e}")
        finally:
            browser.close()


if __name__ == "__main__":
    main()