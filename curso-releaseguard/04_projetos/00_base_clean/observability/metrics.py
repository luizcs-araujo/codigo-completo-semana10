from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
import time

REQUESTS=Counter('releaseguard_http_requests_total','HTTP requests',['method','path','status'])
DURATION=Histogram('releaseguard_http_request_duration_seconds','HTTP duration',['method','path'])
DEPENDENCY=Histogram('releaseguard_dependency_duration_seconds','Dependency duration',['dependency'])

class MetricsMiddleware(BaseHTTPMiddleware):
    async def dispatch(self,request:Request,call_next):
        start=time.perf_counter()
        try:
            response=await call_next(request); status=str(response.status_code); return response
        finally:
            path=request.url.path
            REQUESTS.labels(request.method,path,status if 'status' in locals() else '500').inc()
            DURATION.labels(request.method,path).observe(time.perf_counter()-start)

def metrics_response(): return Response(generate_latest(),media_type=CONTENT_TYPE_LATEST)
