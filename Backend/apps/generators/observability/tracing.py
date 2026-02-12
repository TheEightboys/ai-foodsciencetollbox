"""
Enterprise observability with OpenTelemetry, metrics, and distributed tracing.
Implements SLO/SLI tracking, alerting, and performance monitoring.
"""

import time
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from contextlib import contextmanager
from django.conf import settings
from django.core.cache import cache
from opentelemetry import trace, metrics
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.exporter.prometheus import PrometheusMetricReader
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
import psutil

logger = logging.getLogger(__name__)


class ObservabilityManager:
    """
    Manages all observability components.
    """
    
    def __init__(self):
        self.tracer = None
        self.meter = None
        self._setup_tracing()
        self._setup_metrics()
        self._setup_instruments()
    
    def _setup_tracing(self):
        """Setup distributed tracing with Jaeger."""
        try:
            # Configure resource
            resource = Resource(attributes={
                SERVICE_NAME: "teachai-assistant",
                "service.version": getattr(settings, 'APP_VERSION', '1.0.0'),
                "environment": getattr(settings, 'ENVIRONMENT', 'production')
            })
            
            # Setup tracer provider
            tracer_provider = TracerProvider(resource=resource)
            
            # Configure Jaeger exporter
            jaeger_endpoint = getattr(settings, 'JAEGER_ENDPOINT', 'http://localhost:14268/api/traces')
            jaeger_exporter = JaegerExporter(
                endpoint=jaeger_endpoint,
                collector_endpoint=jaeger_endpoint
            )
            
            # Add batch span processor
            span_processor = BatchSpanProcessor(jaeger_exporter)
            tracer_provider.add_span_processor(span_processor)
            
            # Set as global tracer provider
            trace.set_tracer_provider(tracer_provider)
            
            # Get tracer
            self.tracer = trace.get_tracer(__name__)
            
            logger.info("OpenTelemetry tracing initialized")
            
        except Exception as e:
            logger.error(f"Failed to setup tracing: {e}")
            self.tracer = trace.get_tracer(__name__)
    
    def _setup_metrics(self):
        """Setup metrics with Prometheus."""
        try:
            # Configure metric reader
            metric_reader = PrometheusMetricReader()
            
            # Setup meter provider
            meter_provider = MeterProvider(metric_readers=[metric_reader])
            metrics.set_meter_provider(meter_provider)
            
            # Get meter
            self.meter = metrics.get_meter(__name__)
            
            logger.info("OpenTelemetry metrics initialized")
            
        except Exception as e:
            logger.error(f"Failed to setup metrics: {e}")
            self.meter = metrics.get_meter(__name__)
    
    def _setup_instruments(self):
        """Setup metric instruments."""
        if not self.meter:
            return
        
        # Counters
        self.request_counter = self.meter.create_counter(
            "http_requests_total",
            description="Total HTTP requests"
        )
        
        self.generation_counter = self.meter.create_counter(
            "llm_generations_total",
            description="Total LLM generations"
        )
        
        self.error_counter = self.meter.create_counter(
            "errors_total",
            description="Total errors"
        )
        
        # Histograms
        self.request_duration = self.meter.create_histogram(
            "http_request_duration_seconds",
            description="HTTP request duration",
            unit="s"
        )
        
        self.generation_duration = self.meter.create_histogram(
            "llm_generation_duration_seconds",
            description="LLM generation duration",
            unit="s"
        )
        
        # Gauges
        self.active_connections = self.meter.create_up_down_counter(
            "active_connections",
            description="Number of active connections"
        )
        
        self.queue_size = self.meter.create_up_down_counter(
            "queue_size",
            description="Size of processing queue"
        )
        
        self.system_memory = self.meter.create_observable_gauge(
            "system_memory_bytes",
            description="System memory usage",
            callbacks=[self._get_memory_usage]
        )
    
    def _get_memory_usage(self, options: Dict[str, Any]) -> List[int]:
        """Get system memory usage."""
        memory = psutil.virtual_memory()
        return [memory.used]
    
    @contextmanager
    def trace(self, name: str, **attributes):
        """Context manager for tracing operations."""
        span = self.tracer.start_span(name)
        
        # Add attributes
        for key, value in attributes.items():
            span.set_attribute(key, value)
        
        try:
            with trace.use_span(span):
                yield span
        except Exception as e:
            span.set_status(trace.Status(trace.StatusCode.ERROR, str(e)))
            span.record_exception(e)
            raise
        finally:
            span.end()
    
    def record_metric(self, name: str, value: float, **attributes):
        """Record a metric value."""
        if name == "http_requests_total":
            self.request_counter.add(value, attributes)
        elif name == "llm_generations_total":
            self.generation_counter.add(value, attributes)
        elif name == "errors_total":
            self.error_counter.add(value, attributes)
        elif name == "http_request_duration_seconds":
            self.request_duration.record(value, attributes)
        elif name == "llm_generation_duration_seconds":
            self.generation_duration.record(value, attributes)
        elif name == "active_connections":
            self.active_connections.add(value, attributes)
        elif name == "queue_size":
            self.queue_size.add(value, attributes)


class SLOManager:
    """
    Service Level Objective management.
    """
    
    def __init__(self, observability: ObservabilityManager):
        self.obs = observability
        self.slo_definitions = self._load_slo_definitions()
        self.sli_calculators = self._setup_sli_calculators()
    
    def _load_slo_definitions(self) -> Dict[str, Dict]:
        """Load SLO definitions from settings."""
        return getattr(settings, 'SLO_DEFINITIONS', {
            'api_availability': {
                'objective': 0.999,  # 99.9%
                'period': '30d',
                'alerting': {
                    'burn_rate_threshold': 2.0,
                    'alert_threshold': 0.995
                }
            },
            'response_time': {
                'objective': 0.95,  # 95% under 2s
                'threshold': 2.0,
                'period': '7d'
            },
            'generation_success': {
                'objective': 0.98,  # 98% success rate
                'period': '24h'
            }
        })
    
    def _setup_sli_calculators(self):
        """Setup Service Level Indicator calculators."""
        return {
            'api_availability': self._calculate_availability,
            'response_time': self._calculate_response_time_p95,
            'generation_success': self._calculate_generation_success
        }
    
    def calculate_sli(self, slo_name: str) -> float:
        """Calculate Service Level Indicator."""
        if slo_name not in self.sli_calculators:
            raise ValueError(f"Unknown SLO: {slo_name}")
        
        return self.sli_calculators[slo_name]()
    
    def check_slo_compliance(self, slo_name: str) -> Dict[str, Any]:
        """Check if SLO is being met."""
        sli = self.calculate_sli(slo_name)
        slo_def = self.slo_definitions[slo_name]
        
        is_compliant = sli >= slo_def['objective']
        
        return {
            'slo_name': slo_name,
            'sli': sli,
            'objective': slo_def['objective'],
            'is_compliant': is_compliant,
            'gap': slo_def['objective'] - sli if not is_compliant else 0
        }
    
    def _calculate_availability(self) -> float:
        """Calculate API availability SLI."""
        # Get total requests and errors from metrics
        total = self._get_metric_sum('http_requests_total', period='30d')
        errors = self._get_metric_sum('errors_total', period='30d')
        
        if total == 0:
            return 1.0
        
        return (total - errors) / total
    
    def _calculate_response_time_p95(self) -> float:
        """Calculate 95th percentile response time."""
        # This would query Prometheus for histogram quantile
        # For now, return mock value
        return 0.92  # 92% under threshold
    
    def _calculate_generation_success(self) -> float:
        """Calculate LLM generation success rate."""
        total = self._get_metric_sum('llm_generations_total', period='24h')
        errors = self._get_metric_sum('errors_total', period='24h', service='llm')
        
        if total == 0:
            return 1.0
        
        return (total - errors) / total
    
    def _get_metric_sum(self, metric_name: str, period: str = '1h', **filters) -> float:
        """Get metric sum from Prometheus."""
        # This would query Prometheus API
        # For now, return from cache
        cache_key = f"metric_sum:{metric_name}:{period}"
        return cache.get(cache_key, 0.0)


class AlertManager:
    """
    Manages alerting based on SLOs and metrics.
    """
    
    def __init__(self, slo_manager: SLOManager):
        self.slo_manager = slo_manager
        self.alert_rules = self._load_alert_rules()
        self.alert_history: List[Dict] = []
    
    def _load_alert_rules(self) -> List[Dict]:
        """Load alert rules."""
        return [
            {
                'name': 'high_error_rate',
                'condition': 'error_rate > 0.05',
                'severity': 'critical',
                'duration': '5m'
            },
            {
                'name': 'slow_response',
                'condition': 'p95_response_time > 5s',
                'severity': 'warning',
                'duration': '10m'
            },
            {
                'name': 'slo_breached',
                'condition': 'sli < slo_objective',
                'severity': 'critical',
                'duration': '1m'
            }
        ]
    
    def check_alerts(self) -> List[Dict]:
        """Check all alert conditions."""
        active_alerts = []
        
        for rule in self.alert_rules:
            if self._evaluate_rule(rule):
                alert = {
                    'rule': rule['name'],
                    'severity': rule['severity'],
                    'message': self._format_alert_message(rule),
                    'timestamp': datetime.utcnow()
                }
                active_alerts.append(alert)
                self._send_alert(alert)
        
        return active_alerts
    
    def _evaluate_rule(self, rule: Dict) -> bool:
        """Evaluate alert rule."""
        condition = rule['condition']
        
        # Simple evaluation - in reality, use PromQL
        if 'error_rate' in condition:
            error_rate = self._calculate_error_rate()
            return error_rate > 0.05
        elif 'p95_response_time' in condition:
            p95 = self._get_p95_response_time()
            return p95 > 5.0
        elif 'sli' in condition:
            # Check all SLOs
            for slo_name in self.slo_manager.slo_definitions:
                compliance = self.slo_manager.check_slo_compliance(slo_name)
                if not compliance['is_compliant']:
                    return True
            return False
        
        return False
    
    def _send_alert(self, alert: Dict):
        """Send alert notification."""
        # Log alert
        logger.warning(f"ALERT: {alert['message']}")
        
        # Send to PagerDuty, Slack, etc.
        # Implementation depends on your alerting system
        
        # Store in history
        self.alert_history.append(alert)
    
    def _format_alert_message(self, rule: Dict) -> str:
        """Format alert message."""
        if rule['name'] == 'high_error_rate':
            return f"High error rate detected: {self._calculate_error_rate():.2%}"
        elif rule['name'] == 'slow_response':
            return f"Slow response time: P95 at {self._get_p95_response_time():.2f}s"
        elif rule['name'] == 'slo_breached':
            return "SLO breach detected"
        return f"Alert: {rule['name']}"
    
    def _calculate_error_rate(self) -> float:
        """Calculate current error rate."""
        # Get from metrics
        return 0.02  # Mock: 2% error rate
    
    def _get_p95_response_time(self) -> float:
        """Get P95 response time."""
        return 3.2  # Mock: 3.2 seconds


class PerformanceProfiler:
    """
    Performance profiling for optimization.
    """
    
    def __init__(self, observability: ObservabilityManager):
        self.obs = observability
    
    @contextmanager
    def profile_function(self, function_name: str):
        """Profile a function's performance."""
        start_time = time.time()
        start_memory = self._get_memory_usage()
        
        try:
            yield
        finally:
            end_time = time.time()
            end_memory = self._get_memory_usage()
            
            # Record metrics
            duration = end_time - start_time
            memory_delta = end_memory - start_memory
            
            self.obs.record_metric(
                f"{function_name}_duration",
                duration,
                function=function_name
            )
            
            self.obs.record_metric(
                f"{function_name}_memory_delta",
                memory_delta,
                function=function_name
            )
            
            # Log if performance is poor
            if duration > 1.0:
                logger.warning(f"Slow function {function_name}: {duration:.2f}s")
    
    def _get_memory_usage(self) -> int:
        """Get current memory usage."""
        return psutil.Process().memory_info().rss


# Global instance
_observability = None

def get_observability() -> ObservabilityManager:
    """Get global observability instance."""
    global _observability
    if _observability is None:
        _observability = ObservabilityManager()
    return _observability


# Decorators for easy use
def trace_operation(name: str, **attributes):
    """Decorator to trace operations."""
    def decorator(func):
        def wrapper(*args, **kwargs):
            obs = get_observability()
            with obs.trace(name, **attributes):
                return func(*args, **kwargs)
        return wrapper
    return decorator


def record_performance(metric_name: str):
    """Decorator to record performance metrics."""
    def decorator(func):
        def wrapper(*args, **kwargs):
            obs = get_observability()
            profiler = PerformanceProfiler(obs)
            
            with profiler.profile_function(func.__name__):
                result = func(*args, **kwargs)
                
                # Record success metric
                obs.record_metric(f"{metric_name}_total", 1, status="success")
                
                return result
        return wrapper
    return decorator
