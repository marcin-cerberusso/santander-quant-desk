import os
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.sdk.resources import Resource

def setup_tracing(service_name="santander-bot"):
    """
    Sets up OpenTelemetry tracing.
    """
    resource = Resource.create(attributes={
        "service.name": service_name
    })

    provider = TracerProvider(resource=resource)
    
    # OTLP Exporter - expects a collector at localhost:4317 by default
    # or configured via OTEL_EXPORTER_OTLP_ENDPOINT
    try:
        otlp_exporter = OTLPSpanExporter()
        provider.add_span_processor(BatchSpanProcessor(otlp_exporter))
    except Exception:
        pass # Fail silently if OTLP not available/configured

    # Optional: Console Exporter for debugging (controlled by env var)
    # CAUTION: This will interfere with the TUI if enabled
    if os.getenv("ENABLE_CONSOLE_TRACING", "false").lower() == "true":
        provider.add_span_processor(BatchSpanProcessor(ConsoleSpanExporter()))

    trace.set_tracer_provider(provider)
    
    # Auto-instrument requests library
    RequestsInstrumentor().instrument()
    
    return trace.get_tracer(service_name)

tracer = trace.get_tracer("santander-bot")
