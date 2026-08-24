from __future__ import annotations
from pathlib import Path
import base64, json, os, httpx
from pydantic import BaseModel
from typing import Literal

class VisualTriage(BaseModel):
    change_type: str
    severity: Literal['low','medium','high']
    affected_region: str
    evidence: list[str]
    recommendation: Literal['accept','review','block']

def _b64(path:Path)->str: return base64.b64encode(path.read_bytes()).decode()

def triage(baseline:Path,current:Path,diff:Path,metrics:dict,base_url:str|None=None,model:str|None=None)->VisualTriage:
    endpoint=(base_url or os.getenv('OLLAMA_BASE_URL','http://localhost:11434')).rstrip('/')+'/api/chat'
    model=model or os.getenv('OLLAMA_VISION_MODEL','qwen3-vl:8b')
    schema=VisualTriage.model_json_schema()
    prompt='/no_think\nCompare images in order: baseline, current, diff. Return JSON. Evidence must cite the visible button shift and the metrics. Do not infer functional correctness. Metrics: '+json.dumps(metrics)
    images=[_b64(p) for p in (baseline,current,diff)]
    options={'temperature':0,'num_ctx':int(os.getenv('OLLAMA_NUM_CTX','32768')),'num_predict':2048}
    payload={'model':model,'stream':False,'think':False,'format':schema,'options':options,'messages':[{'role':'user','content':prompt,'images':images}]}
    for _ in range(2):
        r=httpx.post(endpoint,json=payload,timeout=180); r.raise_for_status()
        content=r.json()['message'].get('content','')
        if content.strip(): return VisualTriage.model_validate_json(content)
    raise RuntimeError('vision model returned empty content after retry')
