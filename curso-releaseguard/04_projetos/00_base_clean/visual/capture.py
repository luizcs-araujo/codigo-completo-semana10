from pathlib import Path
from playwright.sync_api import sync_playwright

def capture(url:str, output:Path, executable_path:str|None=None):
    output.parent.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as p:
        browser=p.chromium.launch(headless=True, executable_path=executable_path)
        page=browser.new_page(viewport={
            'width':1280, 'height':800
        }, device_scale_factor=1)
        page.goto(url, wait_until="networkidle")
        page.screenshot(path=str(output), full_page=True)
        browser.close()
    return output

# capture("http://localhost:8000/store/checkout", Path("./screenshots/test.png"))