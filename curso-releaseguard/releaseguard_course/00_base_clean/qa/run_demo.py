import json
from pathlib import Path
from qa.executor import run_plan
from qa.sample_plans import insufficient_stock_plan

def main():
    report=run_plan(insufficient_stock_plan())
    data=report.as_dict(); print(json.dumps(data,ensure_ascii=False,indent=2))
    out=Path('artifacts/day1'); out.mkdir(parents=True,exist_ok=True)
    (out/'functional_report.json').write_text(json.dumps(data,ensure_ascii=False,indent=2))
    raise SystemExit(0 if report.passed else 1)
if __name__=='__main__': main()
