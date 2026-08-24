from __future__ import annotations
import httpx

def query_prometheus(query:str,base_url:str='http://localhost:9090')->dict:
    r=httpx.get(base_url.rstrip('/')+'/api/v1/query',params={'query':query},timeout=5); r.raise_for_status(); return r.json()

def query_jaeger(service:str,base_url:str='http://localhost:16686',limit:int=20)->dict:
    r=httpx.get(base_url.rstrip('/')+'/api/traces',params={'service':service,'limit':limit},timeout=5); r.raise_for_status(); return r.json()

def list_jaeger_services(base_url:str='http://localhost:16686')->dict:
    r=httpx.get(base_url.rstrip('/')+'/api/services',timeout=5); r.raise_for_status(); return r.json()

def get_health(base_url:str='http://localhost:8000')->dict:
    r=httpx.get(base_url.rstrip('/')+'/health',timeout=3); r.raise_for_status()
    data=r.json(); return {'status':data.get('status')}

def get_recent_changes(base_url:str='http://localhost:8000')->dict:
    # Baseline didactic endpoint: scenario is operational state, not the RCA answer.
    return {'deployments':[], 'feature_flags':[]}
