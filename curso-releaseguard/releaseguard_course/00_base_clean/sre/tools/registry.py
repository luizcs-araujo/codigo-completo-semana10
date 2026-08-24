from __future__ import annotations
from sre.tools.clients import query_prometheus, query_jaeger, list_jaeger_services, get_health, get_recent_changes

TOOL_SPECS=[
 {'type':'function','function':{'name':'query_metrics','description':'Query Prometheus. ReleaseGuard exposes releaseguard_dependency_duration_seconds_sum and _count with dependency="payment_provider"; divide sum by count for observed average dependency latency.','parameters':{'type':'object','properties':{'query':{'type':'string'}},'required':['query']}}},
 {'type':'function','function':{'name':'list_trace_services','description':'List actual Jaeger service names before querying traces. Logical incident names may differ from telemetry service.name.','parameters':{'type':'object','properties':{}}}},
 {'type':'function','function':{'name':'query_traces','description':'Query Jaeger traces using an exact service name returned by list_trace_services. Inspect checkout.create and payment.request durations.','parameters':{'type':'object','properties':{'service':{'type':'string'}},'required':['service']}}},
 {'type':'function','function':{'name':'get_service_health','description':'Read current ReleaseGuard health state.','parameters':{'type':'object','properties':{}}}},
 {'type':'function','function':{'name':'get_recent_changes','description':'Read recent deployments and feature flag changes.','parameters':{'type':'object','properties':{}}}},
]

def execute(name,args,urls):
    if name=='query_metrics': return query_prometheus(args['query'],urls['prometheus'])
    if name=='list_trace_services': return list_jaeger_services(urls['jaeger'])
    if name=='query_traces': return query_jaeger(args['service'],urls['jaeger'])
    if name=='get_service_health': return get_health(urls['app'])
    if name=='get_recent_changes': return get_recent_changes(urls['app'])
    raise ValueError('tool not allowlisted: '+name)
