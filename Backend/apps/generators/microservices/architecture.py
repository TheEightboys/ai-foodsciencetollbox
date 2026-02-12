"""
Enterprise microservices architecture with service mesh, API gateway, and event-driven communication.
Implements saga pattern, circuit breaking, and distributed transactions.
"""

import json
import logging
from typing import Dict, Any, Optional, List, Callable
from datetime import datetime
from dataclasses import dataclass, asdict
from enum import Enum
import asyncio
from django.conf import settings
from django.core.serializers.json import DjangoJSONEncoder
import pika
from nameko.rpc import rpc, ServiceRunner
from nameko.web.handlers import http
import consul
from circuit_breaker import CircuitBreaker

logger = logging.getLogger(__name__)


class ServiceType(Enum):
    """Types of services in the microservices architecture."""
    API_GATEWAY = "api-gateway"
    AUTH_SERVICE = "auth-service"
    USER_SERVICE = "user-service"
    GENERATOR_SERVICE = "generator-service"
    CONTENT_SERVICE = "content-service"
    NOTIFICATION_SERVICE = "notification-service"
    ANALYTICS_SERVICE = "analytics-service"
    BILLING_SERVICE = "billing-service"


@dataclass
class ServiceEvent:
    """Represents an event in the system."""
    event_id: str
    event_type: str
    aggregate_id: str
    aggregate_type: str
    data: Dict[str, Any]
    metadata: Dict[str, Any]
    timestamp: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            **asdict(self),
            'timestamp': self.timestamp.isoformat()
        }


class EventStore:
    """
    Event sourcing for audit trail and replay capability.
    """
    
    def __init__(self):
        self.events: List[ServiceEvent] = []
        self.snapshots: Dict[str, Dict] = {}
    
    def save_event(self, event: ServiceEvent):
        """Save an event to the store."""
        self.events.append(event)
        
        # Persist to database
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO event_store (event_id, event_type, aggregate_id, aggregate_type, data, metadata, timestamp)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, [
                event.event_id,
                event.event_type,
                event.aggregate_id,
                event.aggregate_type,
                json.dumps(event.data),
                json.dumps(event.metadata),
                event.timestamp
            ])
        
        logger.info(f"Saved event {event.event_id} of type {event.event_type}")
    
    def get_events(self, aggregate_id: str, from_version: int = 0) -> List[ServiceEvent]:
        """Get events for an aggregate."""
        # Query from database
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT * FROM event_store 
                WHERE aggregate_id = %s 
                ORDER BY timestamp ASC
            """, [aggregate_id])
            
            events = []
            for row in cursor.fetchall():
                event = ServiceEvent(
                    event_id=row[1],
                    event_type=row[2],
                    aggregate_id=row[3],
                    aggregate_type=row[4],
                    data=json.loads(row[5]),
                    metadata=json.loads(row[6]),
                    timestamp=row[7]
                )
                events.append(event)
            
            return events
    
    def save_snapshot(self, aggregate_id: str, data: Dict[str, Any], version: int):
        """Save a snapshot of aggregate state."""
        self.snapshots[aggregate_id] = {
            'data': data,
            'version': version,
            'timestamp': datetime.utcnow()
        }
        
        # Persist to database
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO snapshots (aggregate_id, data, version, timestamp)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (aggregate_id) DO UPDATE SET
                data = EXCLUDED.data,
                version = EXCLUDED.version,
                timestamp = EXCLUDED.timestamp
            """, [aggregate_id, json.dumps(data), version, datetime.utcnow()])


class SagaOrchestrator:
    """
    Implements saga pattern for distributed transactions.
    """
    
    def __init__(self, event_store: EventStore):
        self.event_store = event_store
        self.active_sagas: Dict[str, Dict] = {}
        self.compensation_actions: Dict[str, Callable] = {}
    
    def start_saga(self, saga_id: str, steps: List[Dict]) -> bool:
        """
        Start a saga with multiple steps.
        
        Args:
            saga_id: Unique saga identifier
            steps: List of step definitions
            
        Returns:
            True if saga started successfully
        """
        saga = {
            'id': saga_id,
            'status': 'running',
            'current_step': 0,
            'steps': steps,
            'completed_steps': [],
            'compensation_needed': False
        }
        
        self.active_sagas[saga_id] = saga
        
        # Execute first step
        return self._execute_next_step(saga_id)
    
    def _execute_next_step(self, saga_id: str) -> bool:
        """Execute the next step in the saga."""
        saga = self.active_sagas[saga_id]
        
        if saga['current_step'] >= len(saga['steps']):
            # Saga completed
            saga['status'] = 'completed'
            self._cleanup_saga(saga_id)
            return True
        
        step = saga['steps'][saga['current_step']]
        
        try:
            # Execute step
            result = self._execute_step(step)
            
            # Record success
            saga['completed_steps'].append({
                'step': step,
                'result': result,
                'timestamp': datetime.utcnow()
            })
            
            # Move to next step
            saga['current_step'] += 1
            
            # Continue saga
            return self._execute_next_step(saga_id)
            
        except Exception as e:
            logger.error(f"Saga step failed: {e}")
            # Start compensation
            return self._start_compensation(saga_id)
    
    def _execute_step(self, step: Dict) -> Any:
        """Execute a single saga step."""
        service_name = step['service']
        action = step['action']
        params = step.get('params', {})
        
        # Get service client
        client = self._get_service_client(service_name)
        
        # Execute action with circuit breaker
        breaker = CircuitBreaker(
            failure_threshold=5,
            recovery_timeout=30,
            expected_exception=Exception
        )
        
        @breaker
        def execute():
            return getattr(client, action)(**params)
        
        return execute()
    
    def _start_compensation(self, saga_id: str):
        """Start compensation for failed saga."""
        saga = self.active_sagas[saga_id]
        saga['status'] = 'compensating'
        
        # Execute compensation in reverse order
        for completed_step in reversed(saga['completed_steps']):
            step = completed_step['step']
            if 'compensation' in step:
                try:
                    self._execute_compensation(step['compensation'], completed_step['result'])
                except Exception as e:
                    logger.error(f"Compensation failed: {e}")
        
        saga['status'] = 'failed'
        self._cleanup_saga(saga_id)
    
    def _execute_compensation(self, compensation: Dict, result: Any):
        """Execute a compensation action."""
        service_name = compensation['service']
        action = compensation['action']
        params = compensation.get('params', {})
        params['original_result'] = result
        
        client = self._get_service_client(service_name)
        getattr(client, action)(**params)
    
    def _get_service_client(self, service_name: str):
        """Get client for a service."""
        # This would return a service client
        # For now, return mock
        return ServiceClient(service_name)
    
    def _cleanup_saga(self, saga_id: str):
        """Clean up completed saga."""
        saga = self.active_sagas.pop(saga_id, None)
        if saga:
            # Store saga history
            self.event_store.save_event(ServiceEvent(
                event_id=f"saga-{saga_id}",
                event_type="saga_completed",
                aggregate_id=saga_id,
                aggregate_type="saga",
                data=saga,
                metadata={},
                timestamp=datetime.utcnow()
            ))


class ServiceMesh:
    """
    Service mesh for inter-service communication.
    """
    
    def __init__(self):
        self.services: Dict[str, Dict] = {}
        self.consul = consul.Consul()
        self._register_services()
    
    def _register_services(self):
        """Register all services with Consul."""
        for service_type in ServiceType:
            service_info = {
                'name': service_type.value,
                'id': f"{service_type.value}-1",
                'address': self._get_service_address(service_type),
                'port': self._get_service_port(service_type),
                'health': 'unknown'
            }
            self.services[service_type.value] = service_info
            
            # Register with Consul
            self.consul.agent.service.register(
                name=service_info['name'],
                service_id=service_info['id'],
                address=service_info['address'],
                port=service_info['port'],
                check=consul.Check.http(
                    f"http://{service_info['address']}:{service_info['port']}/health",
                    interval="10s"
                )
            )
    
    def _get_service_address(self, service_type: ServiceType) -> str:
        """Get service address from configuration."""
        return getattr(settings, f'{service_type.value.upper()}_HOST', 'localhost')
    
    def _get_service_port(self, service_type: ServiceType) -> int:
        """Get service port from configuration."""
        return getattr(settings, f'{service_type.value.upper()}_PORT', 8000)
    
    def discover_service(self, service_name: str) -> Optional[Dict]:
        """Discover a service instance."""
        _, services = self.consul.health.service(service_name, passing=True)
        
        if not services:
            return None
        
        # Return first healthy service
        service = services[0]
        return {
            'address': service['Service']['Address'],
            'port': service['Service']['Port']
        }
    
    def get_service_client(self, service_name: str):
        """Get a client for a service."""
        service_info = self.discover_service(service_name)
        if not service_info:
            raise Exception(f"Service {service_name} not available")
        
        return ServiceClient(service_name, service_info)


class ServiceClient:
    """
    Client for communicating with other services.
    """
    
    def __init__(self, service_name: str, service_info: Optional[Dict] = None):
        self.service_name = service_name
        self.service_info = service_info or {}
        self.circuit_breaker = CircuitBreaker(
            failure_threshold=5,
            recovery_timeout=30
        )
    
    @circuit_breaker
    def call(self, method: str, **kwargs):
        """Call a method on the service."""
        # This would make actual HTTP/RPC call
        # For now, return mock response
        return {'status': 'success', 'data': kwargs}


class EventBus:
    """
    Event bus for asynchronous communication.
    """
    
    def __init__(self):
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(
                host=getattr(settings, 'RABBITMQ_HOST', 'localhost')
            )
        )
        self.channel = self.connection.channel()
        
        # Declare exchanges
        self.channel.exchange_declare(
            exchange='teachai.events',
            exchange_type='topic',
            durable=True
        )
        
        # Declare queues
        self.declare_queues()
    
    def declare_queues(self):
        """Declare queues for different event types."""
        queues = [
            'user.created',
            'content.generated',
            'generation.failed',
            'billing.charged'
        ]
        
        for queue in queues:
            self.channel.queue_declare(queue=queue, durable=True)
            self.channel.queue_bind(
                exchange='teachai.events',
                queue=queue,
                routing_key=queue
            )
    
    def publish_event(self, event: ServiceEvent):
        """Publish an event to the bus."""
        self.channel.basic_publish(
            exchange='teachai.events',
            routing_key=event.event_type,
            body=json.dumps(event.to_dict(), cls=DjangoJSONEncoder),
            properties=pika.BasicProperties(
                delivery_mode=2,  # Make message persistent
                message_id=event.event_id
            )
        )
        
        logger.info(f"Published event {event.event_id} to {event.event_type}")
    
    def subscribe_to_events(self, event_types: List[str], handler: Callable):
        """Subscribe to specific event types."""
        def callback(ch, method, properties, body):
            try:
                event_data = json.loads(body)
                event = ServiceEvent(
                    event_id=event_data['event_id'],
                    event_type=event_data['event_type'],
                    aggregate_id=event_data['aggregate_id'],
                    aggregate_type=event_data['aggregate_type'],
                    data=event_data['data'],
                    metadata=event_data['metadata'],
                    timestamp=datetime.fromisoformat(event_data['timestamp'])
                )
                
                handler(event)
                
                # Acknowledge message
                ch.basic_ack(delivery_tag=method.delivery_tag)
                
            except Exception as e:
                logger.error(f"Error processing event: {e}")
                # Negative acknowledge for retry
                ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
        
        # Set up consumer for each event type
        for event_type in event_types:
            self.channel.basic_consume(
                queue=event_type,
                on_message_callback=callback
            )
        
        # Start consuming
        self.channel.start_consuming()


class APIGateway:
    """
    API Gateway for routing and cross-cutting concerns.
    """
    
    def __init__(self, service_mesh: ServiceMesh):
        self.service_mesh = service_mesh
        self.routes = self._load_routes()
        self.middleware_stack = self._build_middleware_stack()
    
    def _load_routes(self) -> Dict[str, Dict]:
        """Load API routes."""
        return {
            '/api/v1/auth/*': {
                'service': 'auth-service',
                'methods': ['POST', 'PUT', 'DELETE']
            },
            '/api/v1/users/*': {
                'service': 'user-service',
                'methods': ['GET', 'POST', 'PUT', 'DELETE']
            },
            '/api/v1/generators/*': {
                'service': 'generator-service',
                'methods': ['GET', 'POST', 'PUT', 'DELETE']
            },
            '/api/v1/content/*': {
                'service': 'content-service',
                'methods': ['GET', 'POST', 'PUT', 'DELETE']
            }
        }
    
    def _build_middleware_stack(self) -> List[Callable]:
        """Build middleware stack."""
        return [
            self._authentication_middleware,
            self._authorization_middleware,
            self._rate_limiting_middleware,
            self._logging_middleware,
            self._metrics_middleware
        ]
    
    def route_request(self, path: str, method: str, headers: Dict, body: Any) -> Dict:
        """Route request to appropriate service."""
        # Find matching route
        service_name = self._find_service_for_path(path)
        
        if not service_name:
            return {'error': 'Not found', 'status': 404}
        
        # Apply middleware
        for middleware in self.middleware_stack:
            result = middleware(path, method, headers, body)
            if result is not None:
                return result
        
        # Forward to service
        client = self.service_mesh.get_service_client(service_name)
        return client.call('handle_request', path=path, method=method, headers=headers, body=body)
    
    def _find_service_for_path(self, path: str) -> Optional[str]:
        """Find which service handles this path."""
        for route_pattern, route_info in self.routes.items():
            if self._match_path(path, route_pattern):
                return route_info['service']
        return None
    
    def _match_path(self, path: str, pattern: str) -> bool:
        """Check if path matches pattern."""
        # Simple pattern matching - in reality, use proper path matching
        if pattern.endswith('*'):
            return path.startswith(pattern[:-1])
        return path == pattern
    
    def _authentication_middleware(self, path: str, method: str, headers: Dict, body: Any) -> Optional[Dict]:
        """Authentication middleware."""
        if path.startswith('/api/v1/auth'):
            return None  # Skip auth for auth endpoints
        
        token = headers.get('Authorization')
        if not token:
            return {'error': 'Authentication required', 'status': 401}
        
        # Validate token
        if not self._validate_token(token):
            return {'error': 'Invalid token', 'status': 401}
        
        return None
    
    def _authorization_middleware(self, path: str, method: str, headers: Dict, body: Any) -> Optional[Dict]:
        """Authorization middleware."""
        # Check user permissions
        return None
    
    def _rate_limiting_middleware(self, path: str, method: str, headers: Dict, body: Any) -> Optional[Dict]:
        """Rate limiting middleware."""
        # Check rate limits
        return None
    
    def _logging_middleware(self, path: str, method: str, headers: Dict, body: Any) -> Optional[Dict]:
        """Logging middleware."""
        logger.info(f"{method} {path}")
        return None
    
    def _metrics_middleware(self, path: str, method: str, headers: Dict, body: Any) -> Optional[Dict]:
        """Metrics middleware."""
        # Record metrics
        return None
    
    def _validate_token(self, token: str) -> bool:
        """Validate JWT token."""
        # Implement JWT validation
        return True


# Global instances
_event_store = None
_saga_orchestrator = None
_service_mesh = None
_event_bus = None
_api_gateway = None

def get_event_store() -> EventStore:
    """Get global event store instance."""
    global _event_store
    if _event_store is None:
        _event_store = EventStore()
    return _event_store

def get_saga_orchestrator() -> SagaOrchestrator:
    """Get global saga orchestrator instance."""
    global _saga_orchestrator
    if _saga_orchestrator is None:
        _saga_orchestrator = SagaOrchestrator(get_event_store())
    return _saga_orchestrator

def get_service_mesh() -> ServiceMesh:
    """Get global service mesh instance."""
    global _service_mesh
    if _service_mesh is None:
        _service_mesh = ServiceMesh()
    return _service_mesh

def get_event_bus() -> EventBus:
    """Get global event bus instance."""
    global _event_bus
    if _event_bus is None:
        _event_bus = EventBus()
    return _event_bus

def get_api_gateway() -> APIGateway:
    """Get global API gateway instance."""
    global _api_gateway
    if _api_gateway is None:
        _api_gateway = APIGateway(get_service_mesh())
    return _api_gateway
