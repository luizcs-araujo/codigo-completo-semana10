from __future__ import annotations
import argparse, json, httpx
from pathlib import Path
from visual.capture import capture
from visual.compare import compare, save_metrics

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--base-url',default='http://127.0.0.1:8000'); ap.add_argument('--chromium',default='/usr/bin/chromium'); args=ap.parse_args()
    out=Path('artifacts/visual'); out.mkdir(parents=True,exist_ok=True)
    httpx.post(args.base_url+'/lab/scenarios/reset').raise_for_status()
    capture(args.base_url+'/store/checkout',out/'baseline.png',args.chromium)
    httpx.post(args.base_url+'/lab/scenarios/visual_checkout_shift/activate').raise_for_status()
    capture(args.base_url+'/store/checkout',out/'current.png',args.chromium)
    metrics=compare(out/'baseline.png',out/'current.png',out/'diff.png'); save_metrics(metrics,out/'metrics.json')
    print(json.dumps(metrics,indent=2)); print('Artifacts:',out.resolve())
if __name__=='__main__': main()
