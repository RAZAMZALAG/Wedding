"""
Comprehensive Logging Configuration for Wedding Planner System
Based on debugging best practices for production applications
"""

import logging
import logging.handlers
import os
import sys
from datetime import datetime
import json
import traceback
from functools import wraps
from flask import request, g
import uuid


class JSONFormatter(logging.Formatter):
    """Custom JSON formatter for structured logging"""
    
    def format(self, record):
        log_entry = {
            'timestamp': datetime.utcfromtimestamp(record.created).isoformat() + 'Z',
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno,
            'thread': record.thread,
            'process': record.process
        }
        
        # Add request context if available
        try:
            if hasattr(g, 'request_id'):
                log_entry['request_id'] = g.request_id
            if hasattr(g, 'user_id'):
                log_entry['user_id'] = g.user_id
            if hasattr(g, 'user_email'):
                log_entry['user_email'] = g.user_email
        except RuntimeError:
            # Outside of Flask application context
            pass
            
        # Add HTTP request details if in request context
        try:
            if request:
                log_entry['http'] = {
                    'method': request.method,
                    'url': request.url,
                    'remote_addr': request.remote_addr,
                    'user_agent': request.headers.get('User-Agent', ''),
                    'content_type': request.content_type
                }
        except RuntimeError:
            # Outside of request context
            pass
        
        # Add exception information if present
        if record.exc_info:
            log_entry['exception'] = {
                'type': record.exc_info[0].__name__,
                'message': str(record.exc_info[1]),
                'traceback': traceback.format_exception(*record.exc_info)
            }
        
        # Add extra fields
        if hasattr(record, 'extra_data'):
            log_entry['data'] = record.extra_data
            
        return json.dumps(log_entry, ensure_ascii=False)


class ColoredConsoleFormatter(logging.Formatter):
    """Colored console formatter for development"""
    
    COLORS = {
        'DEBUG': '\033[36m',      # Cyan
        'INFO': '\033[32m',       # Green
        'WARNING': '\033[33m',    # Yellow
        'ERROR': '\033[31m',      # Red
        'CRITICAL': '\033[35m',   # Magenta
    }
    RESET = '\033[0m'
    
    def format(self, record):
        color = self.COLORS.get(record.levelname, '')
        record.levelname = f"{color}{record.levelname}{self.RESET}"
        
        # Add request context if available
        context_info = ""
        try:
            if hasattr(g, 'request_id'):
                context_info += f" [req:{g.request_id[:8]}]"
            if hasattr(g, 'user_email'):
                context_info += f" [user:{g.user_email}]"
        except RuntimeError:
            # Outside of Flask application context
            pass
            
        formatted = super().format(record)
        if context_info:
            formatted = formatted.replace(record.getMessage(), f"{record.getMessage()}{context_info}")
            
        return formatted


def setup_logging(app_name="wedding_planner", log_level="INFO", log_to_file=True, log_to_console=True):
    """
    Setup comprehensive logging configuration
    
    Args:
        app_name: Application name for log files
        log_level: Minimum log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_to_file: Whether to log to files
        log_to_console: Whether to log to console
    """
    
    # Create logs directory
    log_dir = os.path.join(os.path.dirname(__file__), 'logs')
    os.makedirs(log_dir, exist_ok=True)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level.upper()))
    
    # Clear existing handlers
    root_logger.handlers.clear()
    
    # File handlers with rotation
    if log_to_file:
        # Main application log
        file_handler = logging.handlers.RotatingFileHandler(
            os.path.join(log_dir, f'{app_name}.log'),
            maxBytes=50*1024*1024,  # 50MB
            backupCount=10
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(JSONFormatter())
        root_logger.addHandler(file_handler)
        
        # Error-only log
        error_handler = logging.handlers.RotatingFileHandler(
            os.path.join(log_dir, f'{app_name}_errors.log'),
            maxBytes=20*1024*1024,  # 20MB
            backupCount=5
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(JSONFormatter())
        root_logger.addHandler(error_handler)
        
        # Performance/timing log
        perf_handler = logging.handlers.RotatingFileHandler(
            os.path.join(log_dir, f'{app_name}_performance.log'),
            maxBytes=30*1024*1024,  # 30MB
            backupCount=5
        )
        perf_handler.setLevel(logging.INFO)
        perf_handler.setFormatter(JSONFormatter())
        
        # Create performance logger
        perf_logger = logging.getLogger('performance')
        perf_logger.addHandler(perf_handler)
        perf_logger.propagate = False
    
    # Console handler for development
    if log_to_console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(getattr(logging, log_level.upper()))
        
        # Use colored formatter for console
        console_formatter = ColoredConsoleFormatter(
            '%(asctime)s | %(levelname)s | %(name)s:%(funcName)s:%(lineno)d | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        console_handler.setFormatter(console_formatter)
        root_logger.addHandler(console_handler)


def get_logger(name):
    """Get a logger with the specified name"""
    return logging.getLogger(name)


def log_request_response(f):
    """Decorator to log HTTP requests and responses"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Generate request ID
        request_id = str(uuid.uuid4())
        g.request_id = request_id
        
        logger = get_logger(f.__module__)
        
        # Log request start
        start_time = datetime.utcnow()
        logger.info(
            f"Request started: {request.method} {request.path}",
            extra={'extra_data': {
                'request_id': request_id,
                'method': request.method,
                'path': request.path,
                'query_params': dict(request.args),
                'content_length': request.content_length,
                'start_time': start_time.isoformat()
            }}
        )
        
        try:
            # Execute the function
            response = f(*args, **kwargs)
            
            # Log successful response
            end_time = datetime.utcnow()
            duration_ms = (end_time - start_time).total_seconds() * 1000
            
            status_code = getattr(response, 'status_code', 200)
            logger.info(
                f"Request completed: {status_code} in {duration_ms:.2f}ms",
                extra={'extra_data': {
                    'request_id': request_id,
                    'status_code': status_code,
                    'duration_ms': duration_ms,
                    'end_time': end_time.isoformat()
                }}
            )
            
            # Log to performance logger for slow requests
            if duration_ms > 1000:  # > 1 second
                perf_logger = get_logger('performance')
                perf_logger.warning(
                    f"Slow request detected: {request.method} {request.path} took {duration_ms:.2f}ms",
                    extra={'extra_data': {
                        'request_id': request_id,
                        'method': request.method,
                        'path': request.path,
                        'duration_ms': duration_ms,
                        'status_code': status_code
                    }}
                )
            
            return response
            
        except Exception as e:
            # Log error response
            end_time = datetime.utcnow()
            duration_ms = (end_time - start_time).total_seconds() * 1000
            
            logger.error(
                f"Request failed: {str(e)} after {duration_ms:.2f}ms",
                exc_info=True,
                extra={'extra_data': {
                    'request_id': request_id,
                    'error_type': type(e).__name__,
                    'error_message': str(e),
                    'duration_ms': duration_ms,
                    'end_time': end_time.isoformat()
                }}
            )
            raise
    
    return decorated_function


def log_database_operation(operation_type, collection_name, operation_details=None):
    """Log database operations for monitoring and debugging"""
    logger = get_logger('database')
    
    log_data = {
        'operation_type': operation_type,
        'collection': collection_name,
        'timestamp': datetime.utcnow().isoformat()
    }
    
    if operation_details:
        log_data.update(operation_details)
    
    try:
        if hasattr(g, 'request_id'):
            log_data['request_id'] = g.request_id
    except RuntimeError:
        # Outside of Flask application context
        pass
    
    logger.info(
        f"Database {operation_type} on {collection_name}",
        extra={'extra_data': log_data}
    )


def log_auth_event(event_type, user_email=None, success=True, details=None):
    """Log authentication events for security monitoring"""
    logger = get_logger('auth')
    
    log_data = {
        'event_type': event_type,
        'success': success,
        'timestamp': datetime.utcnow().isoformat(),
        'ip_address': request.remote_addr if request else None
    }
    
    if user_email:
        log_data['user_email'] = user_email
        try:
            g.user_email = user_email  # Store in request context
        except RuntimeError:
            # Outside of Flask application context
            pass
    
    if details:
        log_data.update(details)
    
    try:
        if hasattr(g, 'request_id'):
            log_data['request_id'] = g.request_id
    except RuntimeError:
        # Outside of Flask application context
        pass
    
    level = logging.INFO if success else logging.WARNING
    logger.log(
        level,
        f"Authentication {event_type}: {'success' if success else 'failed'}",
        extra={'extra_data': log_data}
    )


def log_business_event(event_type, details=None):
    """Log important business events (bookings, payments, etc.)"""
    logger = get_logger('business')
    
    log_data = {
        'event_type': event_type,
        'timestamp': datetime.utcnow().isoformat()
    }
    
    if details:
        log_data.update(details)
    
    try:
        if hasattr(g, 'request_id'):
            log_data['request_id'] = g.request_id
        if hasattr(g, 'user_email'):
            log_data['user_email'] = g.user_email
    except RuntimeError:
        # Outside of Flask application context
        pass
    
    logger.info(
        f"Business event: {event_type}",
        extra={'extra_data': log_data}
    )


class PerformanceMonitor:
    """Context manager for monitoring performance of code blocks"""
    
    def __init__(self, operation_name, logger_name='performance'):
        self.operation_name = operation_name
        self.logger = get_logger(logger_name)
        self.start_time = None
    
    def __enter__(self):
        self.start_time = datetime.utcnow()
        self.logger.debug(f"Started {self.operation_name}")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        end_time = datetime.utcnow()
        duration_ms = (end_time - self.start_time).total_seconds() * 1000
        
        if exc_type:
            self.logger.error(
                f"{self.operation_name} failed after {duration_ms:.2f}ms",
                exc_info=(exc_type, exc_val, exc_tb),
                extra={'extra_data': {
                    'operation': self.operation_name,
                    'duration_ms': duration_ms,
                    'error': str(exc_val)
                }}
            )
        else:
            log_level = logging.WARNING if duration_ms > 500 else logging.DEBUG
            self.logger.log(
                log_level,
                f"{self.operation_name} completed in {duration_ms:.2f}ms",
                extra={'extra_data': {
                    'operation': self.operation_name,
                    'duration_ms': duration_ms
                }}
            )


# Convenience functions for common logging patterns
def log_user_action(action, user_email=None, resource_id=None, details=None):
    """Log user actions for audit trail"""
    logger = get_logger('audit')
    
    log_data = {
        'action': action,
        'timestamp': datetime.utcnow().isoformat(),
        'ip_address': request.remote_addr if request else None
    }
    
    if user_email:
        log_data['user_email'] = user_email
    if resource_id:
        log_data['resource_id'] = resource_id
    if details:
        log_data.update(details)
    
    try:
        if hasattr(g, 'request_id'):
            log_data['request_id'] = g.request_id
    except RuntimeError:
        # Outside of Flask application context
        pass
    
    logger.info(
        f"User action: {action}",
        extra={'extra_data': log_data}
    )


# Initialize logging when module is imported
def init_app_logging(app):
    """Initialize logging for Flask app"""
    
    # Determine log level from environment
    log_level = os.environ.get('LOG_LEVEL', 'INFO')
    is_production = os.environ.get('FLASK_ENV') == 'production'
    
    # Setup logging
    setup_logging(
        app_name="wedding_planner",
        log_level=log_level,
        log_to_file=True,
        log_to_console=not is_production  # Only console logging in development
    )
    
    # Configure Flask's logger
    app.logger.setLevel(getattr(logging, log_level.upper()))
    
    # Log application startup
    logger = get_logger('app')
    logger.info(
        "Wedding Planner application starting",
        extra={'extra_data': {
            'log_level': log_level,
            'environment': os.environ.get('FLASK_ENV', 'development'),
            'python_version': sys.version,
            'cwd': os.getcwd()
        }}
    )
