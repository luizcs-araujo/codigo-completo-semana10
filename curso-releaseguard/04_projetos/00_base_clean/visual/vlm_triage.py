from pathlib import Path
import base64, json, os, httpx
from pydantic import BaseModel
from typing import Literal

class VisualTriage(BaseModel):
    change_type: str
    severity: Literal["low", "medium", "high"]
    affected_region: str
    evidence: list[str]
    recommendation: Literal["accept", "review", "block"]

def load_b64_image(path):
    return base64.b64encode(path.read_bytes()).decode()

def triage(baseline:Path, current:Path, diff:Path, metrics:dict, model_url:str|None, model:str):
    endpoint = model_url
    schema=VisualTriage.model_json_schema()
    prompt='Compare images in order: baseline, current, diff. Baseline is the expected image for this page. Current is the image of the page beings tested. Diff is the pixel difference between baseline and current. Return JSON. Evidence must cite any visible differences and the metrics. Do not infer function correctness, the goal is to validate possible visual bugs. Metrics: '+json.dumps(metrics)
    images=[
        load_b64_image(baseline), load_b64_image(current), load_b64_image(diff)
    ]

    options={
        "temperature":0,
        "num_ctx":32000,
        "num_predict":2048
    }

    payload={
        'model':model,
        'stream':False,
        'format':schema,
        'options':options,
        'messages':[{
            'role':'user',
            'content':prompt,
            'images':images
        }]
    }

    r=httpx.post(endpoint, json=payload, timeout=180)
    try:
        r.raise_for_status()
    except httpx.HTTPStatusError as exc:
        raise RuntimeError(
            f"Ollama returned {r.status_code}: {r.text}"
        ) from exc
    content=r.json()['message'].get('content', "")
    if content.strip(): return VisualTriage.model_validate_json(content)
    raise RuntimeError("vision model returned empty content")