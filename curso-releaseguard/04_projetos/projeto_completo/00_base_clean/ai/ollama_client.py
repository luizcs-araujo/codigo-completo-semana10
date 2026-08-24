from __future__ import annotations
import os, httpx

def ollama_health(base_url:str|None=None)->bool:
    url=(base_url or os.getenv('OLLAMA_BASE_URL','http://localhost:11434')).rstrip('/')+'/api/tags'
    try:
        return httpx.get(url,timeout=1.5).status_code==200
    except Exception:
        return False
