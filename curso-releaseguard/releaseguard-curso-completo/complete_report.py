from __future__ import annotations
import json, os
from pathlib import Path
from release.policy import decide

def load(path:Path,default): return json.loads(path.read_text()) if path.exists() else default

def main():
    root=Path(os.getenv('RELEASEGUARD_ARTIFACTS_DIR','artifacts'))
    functional=load(root/'day1/functional_report.json',{'passed':True,'steps':[]})
    metrics=load(root/'visual/metrics.json',{})
    triage=load(root/'visual/vlm_triage.json',{})
    visual={'metrics':metrics,'triage':triage,'policy':'review' if metrics and metrics.get('pixel_change_ratio',0)>0 else 'pass'}
    sre=load(root/'sre/investigation_result.json',{'active_incident':False})
    decision=decide(functional,visual,sre)
    report={'decision':decision.decision,'reasons':decision.reasons,'functional':functional,'visual':visual,'sre':sre}
    out=root/'release'; out.mkdir(parents=True,exist_ok=True)
    (out/'release_report.json').write_text(json.dumps(report,indent=2,ensure_ascii=False))
    lines=[f"# Release decision: {decision.decision}",*['- '+r for r in decision.reasons]]
    (out/'release_report.md').write_text('\n'.join(lines)+'\n')
    print(json.dumps(report,indent=2,ensure_ascii=False))
if __name__=='__main__': main()
