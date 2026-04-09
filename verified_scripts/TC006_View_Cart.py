from playwright.sync_api import sync_playwright


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        try:
            # Add a product first
            page.goto("https://automationexercise.com/products")
            page.hover(".product-image-wrapper:first-child")
            page.locator(".product-image-wrapper:first-child .add-to-cart").first.click()
            page.wait_for_selector("#cartModal", timeout=10000)

            # Click View Cart inside the modal using JavaScript to bypass overlay
            page.evaluate("document.querySelector('#cartModal a[href=\"/view_cart\"]').click()")

            # Check cart has items
            page.wait_for_selector("#cart_info_table tbody tr", timeout=10000)
            items = page.locator("#cart_info_table tbody tr").count()
            if items > 0:
                print("PASSED")
            else:
                print("FAILED: Cart is empty")

        except Exception as e:
            print(f"FAILED: {e}")
        finally:
            browser.close()


if __name__ == "__main__":
    main()