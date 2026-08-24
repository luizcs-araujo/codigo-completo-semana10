from __future__ import annotations
from dataclasses import dataclass

@dataclass
class ReleaseDecision:
    decision:str
    reasons:list[str]

def decide(functional:dict, visual:dict, sre:dict|None=None)->ReleaseDecision:
    reasons=[]
    if not functional.get('passed',False): reasons.append('functional critical test failed')
    triage=visual.get('triage') or {}
    if triage.get('recommendation')=='block': reasons.append('visual regression classified as block')
    if visual.get('policy')=='block': reasons.append('visual policy gate failed')
    if sre and sre.get('active_incident',False): reasons.append('active SLO-impacting incident')
    if reasons: return ReleaseDecision('BLOCK',reasons)
    if triage.get('recommendation')=='review' or visual.get('policy')=='review': return ReleaseDecision('REVIEW',['visual evidence requires human review'])
    return ReleaseDecision('PASS',[])
