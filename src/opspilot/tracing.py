from __future__ import annotations
import functools
try:
    from langsmith import traceable
except Exception:  # pragma: no cover
    traceable = None

def traced(name: str, run_type: str='tool'):
    def decorator(fn):
        if traceable is None:
            return fn
        return traceable(name=name, run_type=run_type)(fn)
    return decorator
