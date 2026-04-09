from playwright.sync_api import sync_playwright


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        try:
            page.goto("https://automationexercise.com/products")
            page.hover(".product-image-wrapper:first-child")
            page.locator(".product-image-wrapper:first-child .add-to-cart").first.click()
            page.wait_for_selector("#cartModal", timeout=10000)
            print("PASSED")

        except Exception as e:
            print(f"FAILED: {e}")
        finally:
            browser.close()


if __name__ == "__main__":
    main()