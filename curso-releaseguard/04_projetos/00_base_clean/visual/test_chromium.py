from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(
        headless=True,
        slow_mo=100,
    )
    print(p.chromium.executable_path)
    page = browser.new_page()
    page.goto("https://example.com")

    page.pause()  # Keeps Chromium open with Playwright Inspector
    browser.close()