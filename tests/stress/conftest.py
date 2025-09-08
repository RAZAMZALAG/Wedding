"""
Stress Testing Configuration
Provides fixtures and utilities for stress testing the Wedding Planner application
"""
import pytest
import sys
import os
import threading
import time
from concurrent.futures import ThreadPoolExecutor
import statistics

# Add the Server directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'Server')))

from main import create_app

@pytest.fixture(scope='session')
def stress_app():
    """Create and configure a new app instance for stress testing"""
    app = create_app()
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False
    # Use a separate stress test database
    app.config['MONGO_URI'] = 'mongodb://localhost:27017/wedding_planner_stress_test'
    
    with app.app_context():
        yield app

@pytest.fixture
def stress_client(stress_app):
    """Create a test client for stress testing"""
    return stress_app.test_client()

@pytest.fixture
def performance_metrics():
    """Fixture to collect and analyze performance metrics"""
    class PerformanceCollector:
        def __init__(self):
            self.response_times = []
            self.status_codes = []
            self.errors = []
            
        def record_request(self, response_time, status_code, error=None):
            self.response_times.append(response_time)
            self.status_codes.append(status_code)
            if error:
                self.errors.append(error)
        
        def get_stats(self):
            if not self.response_times:
                return {}
            
            return {
                'total_requests': len(self.response_times),
                'avg_response_time': statistics.mean(self.response_times),
                'min_response_time': min(self.response_times),
                'max_response_time': max(self.response_times),
                'median_response_time': statistics.median(self.response_times),
                'success_rate': len([s for s in self.status_codes if 200 <= s < 400]) / len(self.status_codes),
                'error_count': len(self.errors),
                'status_code_distribution': {
                    code: self.status_codes.count(code) 
                    for code in set(self.status_codes)
                }
            }
    
    return PerformanceCollector()

@pytest.fixture
def concurrent_executor():
    """Fixture for running concurrent requests"""
    with ThreadPoolExecutor(max_workers=20) as executor:
        yield executor

@pytest.fixture
def load_test_config():
    """Configuration for load testing scenarios"""
    return {
        'light_load': {'users': 5, 'requests_per_user': 10, 'delay': 0.1},
        'medium_load': {'users': 10, 'requests_per_user': 20, 'delay': 0.05},
        'heavy_load': {'users': 20, 'requests_per_user': 30, 'delay': 0.01},
        'spike_load': {'users': 50, 'requests_per_user': 5, 'delay': 0}
    }

@pytest.fixture
def sample_stress_data():
    """Sample data for stress testing"""
    return {
        'login_data': {
            'email': 'stress_test@example.com',
            'password': 'StressTest123'
        },
        'registration_data': {
            'firstName': 'Stress',
            'lastName': 'Test',
            'email': 'stress_test@example.com', 
            'password': 'StressTest123',
            'phone': '1234567890',
            'location': 'הדר'
        },
        'booking_data': {
            'event_date': '2024-12-31',
            'event_time': '19:00',
            'event_type': 'New Year Party',
            'guest_count': 200,
            'location': 'Grand Ballroom',
            'special_requests': 'Stress testing booking',
            'items': []
        }
    }
