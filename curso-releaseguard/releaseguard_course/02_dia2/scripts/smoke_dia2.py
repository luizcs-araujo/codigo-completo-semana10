from __future__ import annotations
import subprocess,time,sys,httpx
from pathlib import Path
from playwright.sync_api import sync_playwright
from visual.compare import compare

def render_html(html:str,path:Path):
    with sync_playwright() as p:
        browser=p.chromium.launch(headless=True)
        page=browser.new_page(viewport={'width':1280,'height':800},device_scale_factor=1)
        page.set_content(html,wait_until='load'); page.screenshot(path=str(path),full_page=True); browser.close()

def main():
    proc=subprocess.Popen([sys.executable,'-m','uvicorn','app.main:app','--host','127.0.0.1','--port','8012'],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
    try:
        for _ in range(50):
            try:
                if httpx.get('http://127.0.0.1:8012/health',timeout=.2).status_code==200: break
            except Exception: time.sleep(.1)
        else: raise RuntimeError('server did not start')
        out=Path('artifacts/visual'); out.mkdir(parents=True,exist_ok=True)
        httpx.post('http://127.0.0.1:8012/lab/scenarios/reset')
        normal=httpx.get('http://127.0.0.1:8012/store/checkout').text
        render_html(normal,out/'baseline.png')
        httpx.post('http://127.0.0.1:8012/lab/scenarios/visual_checkout_shift/activate')
        changed=httpx.get('http://127.0.0.1:8012/store/checkout').text
        render_html(changed,out/'current.png')
        m=compare(out/'baseline.png',out/'current.png',out/'diff.png')
        assert m['pixel_change_ratio']>0 and m['ssim']<1 and (out/'diff.png').exists()
        print('SMOKE DIA2 PASS (browser rendered live FastAPI HTML):',m)
    finally:
        proc.terminate(); proc.wait(timeout=5)
if __name__=='__main__': main()
