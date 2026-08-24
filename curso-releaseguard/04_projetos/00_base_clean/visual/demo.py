import argparse, json, httpx
from pathlib import Path
from visual.capture import capture
from visual.compare import compare, save_metrics
from visual.vlm_triage import triage

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--base_url', default="http://127.0.0.1:8000")
    ap.add_argument('--chromium', default='/Users/luizcls/Library/Caches/ms-playwright/chromium-1234/chrome-mac-arm64/Google Chrome for Testing.app/Contents/MacOS/Google Chrome for Testing')
    args = ap.parse_args()
    out = Path('./artifacts/visual')
    out.mkdir(parents=True, exist_ok=True)

    httpx.post(args.base_url+'/lab/scenarios/reset').raise_for_status()
    capture(args.base_url+'/store/checkout', out/'baseline.png', args.chromium)
    httpx.post(args.base_url+'/lab/scenarios/visual_checkout_shift/activate').raise_for_status()
    capture(args.base_url+'/store/checkout', out/'current.png', args.chromium)
    metrics=compare(out/'baseline.png', out/'current.png',out/'diff.png')
    save_metrics(metrics, out/'metrics.json')

def visual_model():
    r=Path('artifacts/visual')
    m=json.loads((r/'metrics.json').read_text())
    result=triage(r/'baseline.png',r/'current.png',r/'diff.png',m, "http://localhost:11434/api/chat", "qwen3-vl:8b")
    print(result.model_dump_json(indent=2))
    (r/'vlm_triage.json').write_text(result.model_dump_json(indent=2))

if __name__=='__main__': 
    main()
    visual_model()