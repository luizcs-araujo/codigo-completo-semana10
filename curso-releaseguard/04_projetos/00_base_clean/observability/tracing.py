from __future__ import annotations
import os
from opentelemetry import trace
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

_configured=False
def configure_tracing():
    global _configured
    if _configured: return trace.get_tracer('releaseguard')
    provider=TracerProvider(resource=Resource.create({'service.name':'releaseguard'})); trace.set_tracer_provider(provider)
    endpoint=os.getenv('OTEL_EXPORTER_OTLP_ENDPOINT')
    if endpoint:
        from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
        provider.add_span_processor(BatchSpanProcessor(OTLPSpanExporter(endpoint=endpoint.rstrip('/')+'/v1/traces')))
    _configured=True
    return trace.get_tracer('releaseguard')
tracer=configure_tracing()
