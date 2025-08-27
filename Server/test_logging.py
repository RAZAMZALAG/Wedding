"""
Test script to validate the comprehensive logging system implementation.
This script demonstrates all logging features and tests their functionality.
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from logger_config import (
    setup_logging, get_logger, log_request_response, PerformanceMonitor,
    log_database_operation, log_auth_event, log_business_event, log_user_action
)
import time
import json

def test_logging_system():
    """Test all aspects of the logging system"""
    
    print("🔧 Setting up logging system...")
    setup_logging("test_wedding_planner", "DEBUG", True, True)
    
    # Get different loggers
    app_logger = get_logger("app")
    auth_logger = get_logger("auth")
    db_logger = get_logger("database")
    perf_logger = get_logger("performance")
    
    print("✅ Logging system initialized\n")
    
    # Test basic logging levels
    print("📝 Testing basic logging levels...")
    app_logger.debug("This is a debug message")
    app_logger.info("This is an info message")
    app_logger.warning("This is a warning message")
    app_logger.error("This is an error message")
    app_logger.critical("This is a critical message")
    print("✅ Basic logging levels tested\n")
    
    # Test structured logging with extra data
    print("📊 Testing structured logging...")
    app_logger.info("User action performed", extra={'extra_data': {
        'user_id': '12345',
        'action': 'login',
        'timestamp': '2025-01-20T10:30:00Z',
        'ip_address': '192.168.1.100'
    }})
    print("✅ Structured logging tested\n")
    
    # Test performance monitoring
    print("⏱️ Testing performance monitoring...")
    with PerformanceMonitor("Database query test"):
        time.sleep(0.1)  # Simulate work
        
    with PerformanceMonitor("Slow operation test"):
        time.sleep(0.6)  # Simulate slow operation (should trigger warning)
    print("✅ Performance monitoring tested\n")
    
    # Test specialized logging functions
    print("🔐 Testing authentication logging...")
    log_auth_event("login_attempt", "test@example.com", True, {"method": "password"})
    log_auth_event("login_failed", "test@example.com", False, {"reason": "invalid_password"})
    print("✅ Authentication logging tested\n")
    
    print("🗄️ Testing database operation logging...")
    log_database_operation("insert", "users", {
        "user_id": "67890",
        "operation_details": {"new_user": True}
    })
    log_database_operation("update", "orders", {
        "order_id": "order_123",
        "status_change": "pending -> approved"
    })
    print("✅ Database operation logging tested\n")
    
    print("👤 Testing user action logging...")
    log_user_action("item_added_to_cart", "test@example.com", "item_456", {
        "item_name": "Wedding Chairs",
        "quantity": 50
    })
    print("✅ User action logging tested\n")
    
    print("💼 Testing business event logging...")
    log_business_event("booking_created", {
        "booking_id": "booking_789",
        "user_email": "test@example.com",
        "total_amount": 2500.00,
        "items_count": 5
    })
    print("✅ Business event logging tested\n")
    
    # Test exception logging
    print("❌ Testing exception logging...")
    try:
        # Intentionally cause an exception
        result = 1 / 0
    except Exception as e:
        app_logger.error("Test exception occurred", exc_info=True, extra={'extra_data': {
            'test_case': 'division_by_zero',
            'user_input': {'numerator': 1, 'denominator': 0}
        }})
    print("✅ Exception logging tested\n")
    
    # Test different logger categories
    print("🏷️ Testing different logger categories...")
    get_logger("models.User").info("User model operation completed")
    get_logger("auth.login").info("Login process initiated")
    get_logger("items.catalog").info("Catalog query executed")
    get_logger("bookings.orders").info("Order processing started")
    print("✅ Logger categories tested\n")
    
    print("🎉 All logging system tests completed successfully!")
    print("📁 Check the 'logs' directory for log files:")
    print("   - wedding_planner.log (all logs)")
    print("   - wedding_planner_errors.log (errors only)")
    print("   - wedding_planner_performance.log (performance metrics)")


if __name__ == "__main__":
    test_logging_system()
