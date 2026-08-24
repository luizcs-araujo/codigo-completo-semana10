from __future__ import annotations
import json, os, string, httpx
from qa.schemas import TestPlan

SYSTEM_INSTRUCTIONS = """Você é um engenheiro de QA. Gere um plano HTTP mínimo, seguro e diretamente executável. Use somente paths, métodos, corpos e status documentados no OpenAPI fornecido. Use valores concretos do contexto de execução; apenas cart_id e order_id podem ser placeholders, depois dos passos que os criam. O oracle deve estar ancorado no requisito ou no contrato, nunca inventado. Retorne somente o schema solicitado."""

def _semantic_issues(plan:TestPlan,openapi:dict)->list[str]:
    issues=[]; available=set(); formatter=string.Formatter()
    for step in plan.steps:
        operation=openapi.get('paths',{}).get(step.path,{}).get(step.method.lower())
        if operation is None: issues.append(f'{step.method} {step.path} is not in OpenAPI'); continue
        documented=operation.get('responses',{})
        if str(step.expect_status) not in documented: issues.append(f'{step.method} {step.path} status {step.expect_status} is not documented')
        if operation.get('requestBody',{}).get('required') and step.json_body is None: issues.append(f'{step.method} {step.path} requires json_body')
        variables={name for _,name,_,_ in formatter.parse(step.path) if name}
        missing=variables-available
        if missing: issues.append(f'{step.path} uses unavailable placeholders: {sorted(missing)}')
        if step.method=='POST' and step.path=='/cart': available.add('cart_id')
        if step.method=='POST' and step.path=='/checkout': available.add('order_id')
    return issues

def generate_plan(requirement:str, openapi:dict, base_url:str|None=None, model:str|None=None, runtime_context:dict|None=None)->TestPlan:
    endpoint=(base_url or os.getenv('OLLAMA_BASE_URL','http://localhost:11434')).rstrip('/')+'/api/chat'
    model=model or os.getenv('OLLAMA_TEXT_MODEL','qwen3:8b')
    schema=TestPlan.model_json_schema()
    prompt=f"Requisito:\n{requirement}\n\nContexto de execução:\n{json.dumps(runtime_context or {},ensure_ascii=False)}\n\nOpenAPI:\n{json.dumps(openapi,ensure_ascii=False)[:24000]}\n\nJSON Schema:\n{json.dumps(schema,ensure_ascii=False)}"
    messages=[{'role':'system','content':SYSTEM_INSTRUCTIONS},{'role':'user','content':prompt}]
    for _ in range(3):
        payload={'model':model,'stream':False,'format':schema,'options':{'temperature':0},'messages':messages}
        r=httpx.post(endpoint,json=payload,timeout=120.0); r.raise_for_status()
        content=r.json()['message']['content']; plan=TestPlan.model_validate_json(content)
        issues=_semantic_issues(plan,openapi)
        if not issues: return plan
        messages.extend([{'role':'assistant','content':content},{'role':'user','content':'Corrija estes problemas semânticos: '+'; '.join(issues)}])
    raise ValueError('generated plan failed semantic validation: '+'; '.join(issues))

def main():
    openapi=httpx.get('http://127.0.0.1:8000/openapi.json',timeout=5).json()
    req='Um usuário não pode adicionar ao carrinho uma quantidade maior que o estoque disponível.'
    products=httpx.get('http://127.0.0.1:8000/products',timeout=5).json()
    plan=generate_plan(req,openapi,runtime_context={'products':products})
    print(plan.model_dump_json(indent=2))
if __name__=='__main__': main()
