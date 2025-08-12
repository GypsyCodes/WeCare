"""
Monitoring and metrics utilities
"""
from prometheus_client import Counter, Histogram, Gauge, Info
from functools import wraps
import time
from typing import Callable, Any


# Define metrics
REQUEST_COUNT = Counter(
    'wecare_http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status_code']
)

REQUEST_DURATION = Histogram(
    'wecare_http_request_duration_seconds',
    'HTTP request duration in seconds',
    ['method', 'endpoint']
)

DATABASE_OPERATIONS = Counter(
    'wecare_database_operations_total',
    'Total database operations',
    ['operation', 'table', 'status']
)

CHECKIN_OPERATIONS = Counter(
    'wecare_checkin_operations_total',
    'Total check-in operations',
    ['status', 'location_valid']
)

DOCUMENT_PROCESSING = Counter(
    'wecare_document_processing_total',
    'Total document processing operations',
    ['document_type', 'status']
)

CELERY_TASK_DURATION = Histogram(
    'wecare_celery_task_duration_seconds',
    'Celery task duration in seconds',
    ['task_name', 'status']
)

ACTIVE_USERS = Gauge(
    'wecare_active_users_total',
    'Number of active users by type',
    ['user_type']
)

SYSTEM_INFO = Info(
    'wecare_system',
    'System information'
)

# Error counters
ERROR_COUNT = Counter(
    'wecare_errors_total',
    'Total errors',
    ['error_type', 'endpoint']
)


def track_request_metrics(func: Callable) -> Callable:
    """Decorator to track request metrics"""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        start_time = time.time()
        status_code = "200"
        
        try:
            result = await func(*args, **kwargs)
            return result
        except Exception as e:
            status_code = getattr(e, 'status_code', '500')
            ERROR_COUNT.labels(
                error_type=type(e).__name__,
                endpoint=func.__name__
            ).inc()
            raise
        finally:
            duration = time.time() - start_time
            REQUEST_DURATION.labels(
                method="unknown",  # Would need to extract from request
                endpoint=func.__name__
            ).observe(duration)
            
            REQUEST_COUNT.labels(
                method="unknown",
                endpoint=func.__name__,
                status_code=str(status_code)
            ).inc()
    
    return wrapper


def track_database_operation(operation: str, table: str):
    """Track database operation"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                result = await func(*args, **kwargs)
                DATABASE_OPERATIONS.labels(
                    operation=operation,
                    table=table,
                    status="success"
                ).inc()
                return result
            except Exception as e:
                DATABASE_OPERATIONS.labels(
                    operation=operation,
                    table=table,
                    status="error"
                ).inc()
                raise
        
        return wrapper
    return decorator


def track_celery_task(task_name: str):
    """Track Celery task execution"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            status = "success"
            
            try:
                result = func(*args, **kwargs)
                return result
            except Exception as e:
                status = "error"
                raise
            finally:
                duration = time.time() - start_time
                CELERY_TASK_DURATION.labels(
                    task_name=task_name,
                    status=status
                ).observe(duration)
        
        return wrapper
    return decorator


def record_checkin_attempt(status: str, location_valid: bool):
    """Record check-in attempt"""
    CHECKIN_OPERATIONS.labels(
        status=status,
        location_valid=str(location_valid).lower()
    ).inc()


def record_document_processing(document_type: str, status: str):
    """Record document processing attempt"""
    DOCUMENT_PROCESSING.labels(
        document_type=document_type,
        status=status
    ).inc()


def update_active_users_count(user_counts: dict):
    """Update active users gauge"""
    for user_type, count in user_counts.items():
        ACTIVE_USERS.labels(user_type=user_type).set(count)


def set_system_info(version: str, environment: str):
    """Set system information"""
    SYSTEM_INFO.info({
        'version': version,
        'environment': environment,
        'application': 'we-care'
    })


# Health check metrics
HEALTH_CHECK = Gauge(
    'wecare_health_check',
    'Health check status',
    ['component']
)


def update_health_status(component: str, healthy: bool):
    """Update health status for a component"""
    HEALTH_CHECK.labels(component=component).set(1 if healthy else 0) 