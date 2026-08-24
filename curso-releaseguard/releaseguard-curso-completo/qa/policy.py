from urllib.parse import urljoin, urlparse
from qa.schemas import TestPlan
ALLOWED_METHODS={'GET','POST'}
ALLOWED_PREFIXES=('/products','/cart','/checkout','/payments','/orders','/lab/scenarios')

def validate_plan_policy(plan:TestPlan, base_url:str)->None:
    parsed=urlparse(base_url)
    if parsed.hostname not in {'127.0.0.1','localhost','host.docker.internal'}:
        raise ValueError('base_url host is not allowlisted')
    for step in plan.steps:
        if step.method not in ALLOWED_METHODS: raise ValueError(f'method not allowed: {step.method}')
        if not step.path.startswith(ALLOWED_PREFIXES): raise ValueError(f'path not allowed: {step.path}')
