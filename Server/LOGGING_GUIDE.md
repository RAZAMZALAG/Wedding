# 📊 Comprehensive Logging System Documentation

## Overview

The Wedding Planner application now includes a professional-grade logging system designed for debugging, monitoring, and production support. This system provides structured JSON logging, multiple log levels, performance monitoring, and specialized logging for different aspects of the application.

## ✨ Key Features

- **Structured JSON Logging**: All logs are output in JSON format for easy parsing and analysis
- **Multiple Log Files**: Separate files for general logs, errors, and performance metrics
- **Request Tracking**: Automatic request ID generation for tracing requests across the system
- **User Context**: Logs include user information when available
- **Performance Monitoring**: Built-in timing and performance tracking
- **Colored Console Output**: Development-friendly colored console logs
- **Log Rotation**: Automatic log file rotation to prevent disk space issues
- **Exception Tracking**: Comprehensive exception logging with stack traces

## 📁 Log File Structure

The system creates logs in the `Server/logs/` directory:

```
Server/logs/
├── wedding_planner.log              # All logs (DEBUG, INFO, WARNING, ERROR, CRITICAL)
├── wedding_planner_errors.log       # Error and critical logs only
└── wedding_planner_performance.log  # Performance and timing logs
```

## 🚀 Quick Start

### Basic Logging

```python
from logger_config import get_logger

# Get a logger for your module
logger = get_logger(__name__)

# Log at different levels
logger.debug("Detailed debugging information")
logger.info("General information about application flow")
logger.warning("Something unexpected happened, but not critical")
logger.error("An error occurred that needs attention")
logger.critical("Critical error that may cause application failure")
```

### Structured Logging with Extra Data

```python
logger.info("User performed action", extra={'extra_data': {
    'user_id': '12345',
    'action': 'login',
    'ip_address': request.remote_addr,
    'timestamp': datetime.utcnow().isoformat()
}})
```

## 🛠️ Specialized Logging Functions

### Authentication Events

```python
from logger_config import log_auth_event

# Successful login
log_auth_event("login_success", "user@example.com", True, {
    "method": "password",
    "user_id": user_id
})

# Failed login attempt
log_auth_event("login_failed", "user@example.com", False, {
    "reason": "invalid_credentials"
})
```

### Database Operations

```python
from logger_config import log_database_operation

log_database_operation("insert", "users", {
    "user_id": new_user_id,
    "operation_details": {"new_registration": True}
})

log_database_operation("update", "orders", {
    "order_id": order_id,
    "status_change": "pending -> approved"
})
```

### User Actions (Audit Trail)

```python
from logger_config import log_user_action

log_user_action("item_added_to_cart", "user@example.com", "item_123", {
    "item_name": "Wedding Chairs",
    "quantity": 50,
    "price": 25.00
})
```

### Business Events

```python
from logger_config import log_business_event

log_business_event("booking_created", {
    "booking_id": booking_id,
    "user_email": user_email,
    "total_amount": 2500.00,
    "items_count": 5,
    "event_date": "2025-09-15"
})
```

### Performance Monitoring

```python
from logger_config import PerformanceMonitor

# Monitor a code block
with PerformanceMonitor("Database query execution"):
    results = complex_database_query()
    
# Monitor slow operations (automatically warns if > 500ms)
with PerformanceMonitor("Image processing"):
    processed_image = process_large_image()
```

## 🎯 Request Context Integration

The logging system automatically includes request context when running within a Flask application:

- **Request ID**: Unique identifier for each HTTP request
- **User Information**: Email and user ID when authenticated
- **HTTP Details**: Method, URL, IP address, user agent

Example log entry with full context:
```json
{
  "timestamp": "2025-08-27T17:55:03.123456Z",
  "level": "INFO",
  "logger": "auth",
  "message": "User login successful",
  "module": "auth",
  "function": "login_user",
  "line": 45,
  "request_id": "abc123de-456f-789g-hij0-123456789012",
  "user_email": "user@example.com",
  "user_id": "user_123",
  "http": {
    "method": "POST",
    "url": "https://example.com/api/auth/login",
    "remote_addr": "192.168.1.100",
    "user_agent": "Mozilla/5.0...",
    "content_type": "application/json"
  },
  "data": {
    "login_method": "password",
    "success": true
  }
}
```

## 📊 Log Levels Guide

| Level    | When to Use | Examples |
|----------|-------------|----------|
| `DEBUG`  | Detailed diagnostic information | Variable values, execution flow |
| `INFO`   | General application flow | Request completed, user actions |
| `WARNING` | Unexpected but handled situations | Deprecated API usage, recoverable errors |
| `ERROR`  | Error conditions that need attention | Failed database queries, API errors |
| `CRITICAL` | Critical errors causing system failure | Database connection lost, critical service down |

## 🔧 Configuration

The logging system can be configured through environment variables:

```bash
# Set log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
export LOG_LEVEL=INFO

# Environment (affects console logging)
export FLASK_ENV=production  # Disables console logging in production
```

## 📈 Production Considerations

### Log Rotation
- Log files automatically rotate when they reach 50MB (main log) or 20MB (error log)
- Up to 10 backup files are kept for main logs, 5 for error logs
- Old log files are automatically compressed and archived

### Performance Impact
- JSON formatting has minimal performance overhead
- File I/O is asynchronous where possible
- Console logging is disabled in production by default

### Security
- User passwords and sensitive data are never logged
- Personal information is logged only when necessary for debugging
- Log files should be secured with appropriate file permissions

## 🔍 Log Analysis Examples

### Finding All Errors for a Specific User
```bash
grep '"user_email":"user@example.com"' wedding_planner_errors.log
```

### Tracking a Specific Request
```bash
grep '"request_id":"abc123de"' wedding_planner.log
```

### Performance Analysis
```bash
# Find slow operations (> 1 second)
grep '"duration_ms":[1-9][0-9][0-9][0-9]' wedding_planner_performance.log
```

### Authentication Failures
```bash
grep '"event_type":"login_failed"' wedding_planner.log
```

## 🚨 Troubleshooting

### Common Issues

1. **Logging errors about Flask context**
   - This happens when logging outside of a Flask request
   - The system handles this gracefully and continues logging

2. **Log files not created**
   - Check that the application has write permissions to the `logs` directory
   - Ensure sufficient disk space is available

3. **Performance impact**
   - If logging is impacting performance, increase the log level to WARNING or ERROR
   - Consider using log aggregation services for high-volume applications

### Best Practices

1. **Use appropriate log levels** - Don't log everything at INFO level
2. **Include context** - Always include relevant IDs and user information
3. **Structure your data** - Use the `extra_data` parameter for complex information
4. **Monitor log file sizes** - Set up alerts for unusual log growth
5. **Regular cleanup** - Implement log archival policies for long-term storage

## 🔗 Integration with Monitoring Tools

The structured JSON format makes it easy to integrate with monitoring and analysis tools:

- **ELK Stack (Elasticsearch, Logstash, Kibana)**: Direct JSON ingestion
- **Splunk**: Native JSON support for indexing and searching
- **Datadog**: Log aggregation and alerting
- **Grafana**: Visualization and dashboards
- **CloudWatch**: AWS log aggregation and monitoring

## 📝 Examples in the Codebase

The logging system is already integrated throughout the application:

- **Authentication** (`auth.py`): Login attempts, registration, token validation
- **User Management** (`users.py`): User CRUD operations, admin actions
- **Items/Catalog** (`items.py`): Item queries, availability checks
- **Bookings** (`bookings.py`): Order processing, status changes
- **AI Assistant** (`ai_assistant.py`): Query processing, API interactions
- **Database** (`models.py`): Database initialization, connection issues

## 🎉 Benefits

1. **Faster Debugging**: Structured logs with request tracing
2. **Better Monitoring**: Performance metrics and business event tracking
3. **Audit Compliance**: Complete audit trail of user actions
4. **Production Support**: Detailed error information for quick resolution
5. **Analytics Ready**: JSON format ready for analysis tools
6. **Scalable**: Designed for high-volume production environments

This logging system provides enterprise-grade observability for the Wedding Planner application, making it easier to debug issues, monitor performance, and maintain the system in production.
