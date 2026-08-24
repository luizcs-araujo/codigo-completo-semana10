from __future__ import annotations
import json, os, httpx
from pydantic import ValidationError
from sre.schemas import Incident, InvestigationResult
from sre.tools.registry import TOOL_SPECS, execute

SYSTEM = (
    "You are a read-only SRE investigator. Form hypotheses, request only evidence "
    "needed to test them, revise hypotheses when evidence contradicts them, and "
    "distinguish symptom, correlation, probable cause, and verified root cause. "
    "Never claim a verified root cause unless evidence directly supports it. "
    "You may propose remediation but all mutations require human approval. "
    "Before concluding a investigation, query the documented ReleaseGuard dependency metric, "
    "list Jaeger services, and query traces using the discovered service name. Do not assume the logical incident service equals service.name. "
    "Prometheus histogram _sum is cumulative seconds, never an average by itself; average equals _sum divided by _count. "
    "Jaeger span duration is in microseconds and seconds equal microseconds divided by 1,000,000. Preserve units and verify arithmetic."
)

def _finalize(endpoint:str,model:str,options:dict,messages:list[dict])->InvestigationResult:
    schema=InvestigationResult.model_json_schema()
    final_messages=messages+[{'role':'user','content':(
        'Return compact final investigation JSON matching this schema: '+json.dumps(schema)+
        '. Include only concise evidence summaries. Set evidence.raw to null or a small '
        'object with the decisive metric/span values; never copy full Prometheus or Jaeger payloads. '
        'Use probable-cause language, keep remediation as proposals, and require human approval. '
        'Never call a Prometheus _sum an average unless you divide by _count. Jaeger duration is '
        'in microseconds; divide by 1,000,000 for seconds and keep the original value.'
    )}]
    final_options={**options,'num_predict':4096}
    last_error='empty response'
    for _ in range(2):
        rr=httpx.post(endpoint,json={'model':model,'stream':False,'think':False,'options':final_options,'format':schema,'messages':final_messages},timeout=180)
        rr.raise_for_status(); content=rr.json()['message'].get('content','')
        if not content.strip():
            continue
        try:
            return InvestigationResult.model_validate_json(content)
        except (ValidationError, ValueError) as exc:
            last_error=str(exc)
            final_messages.extend([
                {'role':'assistant','content':content},
                {'role':'user','content':(
                    'The previous JSON was invalid or truncated. Return a complete, compact JSON '
                    'object now. Omit verbose raw telemetry and preserve only decisive values.'
                )},
            ])
    raise RuntimeError('text model failed final investigation after retry: '+last_error)

def investigate(incident:Incident,max_steps:int=6,model:str|None=None,ollama_url:str|None=None,urls:dict|None=None)->InvestigationResult:
    model=model or os.getenv('OLLAMA_TEXT_MODEL','qwen3:8b')
    endpoint=(ollama_url or os.getenv('OLLAMA_BASE_URL','http://localhost:11434')).rstrip('/')+'/api/chat'
    urls=urls or {'prometheus':'http://localhost:9090','jaeger':'http://localhost:16686','app':'http://localhost:8000'}
    messages=[{'role':'system','content':SYSTEM},{'role':'user','content':incident.model_dump_json()}]
    options={'temperature':0,'num_ctx':int(os.getenv('OLLAMA_NUM_CTX','32768')),'num_predict':2048}
    for _ in range(max_steps):
        payload={'model':model,'stream':False,'think':False,'options':options,'messages':messages,'tools':TOOL_SPECS}
        r=httpx.post(endpoint,json=payload,timeout=120); r.raise_for_status()
        msg=r.json()['message']; messages.append(msg)
        calls=msg.get('tool_calls') or []
        if not calls:
            return _finalize(endpoint,model,options,messages)
        for call in calls:
            fn=call['function']['name']; args=call['function'].get('arguments',{})
            result=execute(fn,args,urls)
            messages.append({'role':'tool','tool_name':fn,'content':json.dumps(result)[:16000]})
    return _finalize(endpoint,model,options,messages)
