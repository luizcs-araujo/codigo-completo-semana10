import json, os, subprocess, sys, tempfile
from pathlib import Path
def main():
    with tempfile.TemporaryDirectory(prefix='releaseguard-smoke-') as tmp:
        root=Path(tmp); (root/'day1').mkdir(); (root/'visual').mkdir(); (root/'sre').mkdir()
        (root/'day1/functional_report.json').write_text(json.dumps({'passed':True,'steps':[]}))
        (root/'visual/metrics.json').write_text(json.dumps({'pixel_change_ratio':0.0,'ssim':1.0}))
        (root/'visual/vlm_triage.json').write_text(json.dumps({'recommendation':'accept'}))
        (root/'sre/investigation_result.json').write_text(json.dumps({'active_incident':False}))
        env={**os.environ,'RELEASEGUARD_ARTIFACTS_DIR':str(root)}
        subprocess.run([sys.executable,'-m','complete_report'],check=True,env=env)
        report=json.loads((root/'release/release_report.json').read_text()); assert report['decision']=='PASS'
        (root/'sre/investigation_result.json').write_text(json.dumps({'active_incident':True}))
        subprocess.run([sys.executable,'-m','complete_report'],check=True,env=env)
        report=json.loads((root/'release/release_report.json').read_text()); assert report['decision']=='BLOCK'
    print('SMOKE COMPLETE PASS: policy produced PASS and BLOCK from evidence')
if __name__=='__main__': main()
