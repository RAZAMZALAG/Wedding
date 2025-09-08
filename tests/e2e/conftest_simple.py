"""
Simplified End-to-End Test Configuration
Provides basic fixtures for E2E testing without complex dependencies
"""
import pytest
import sys
import os

# Add the Server directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'Server')))

from main import app

@pytest.fixture(scope='session')
def e2e_app():
    """Create and configure a new app instance for each test session"""
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False
    # Use a separate test database
    app.config['MONGODB_SETTINGS'] = {
        'db': 'wedding_planner_test_e2e_simple',
        'host': 'mongodb://localhost:27017/',
        'connect': False
    }
    
    with app.app_context():
        yield app

@pytest.fixture
def e2e_client(e2e_app):
    """Create a test client for E2E testing"""
    return e2e_app.test_client()

@pytest.fixture
def sample_user_data():
    """Sample user data for testing (without file upload)"""
    return {
        'firstName': 'Test',
        'lastName': 'User', 
        'email': 'testuser@example.com',
        'password': 'securepass123',
        'phone': '1234567890',
        'location': 'הדר'
    }

@pytest.fixture
def sample_login_data():
    """Sample login data for testing"""
    return {
        'email': 'testuser@example.com',
        'password': 'securepass123'
    }

@pytest.fixture
def sample_item_data():
    """Sample item data for testing"""
    return {
        'name': 'Test Wedding Item',
        'category': 'Decorations',
        'subcategory': 'Centerpieces', 
        'price_per_day': 50.0,
        'description': 'A beautiful test item for weddings',
        'quantity_available': 10,
        'is_available': True
    }

@pytest.fixture
def sample_booking_data():
    """Sample booking data for testing"""
    return {
        'event_date': '2024-12-25',
        'event_time': '18:00',
        'event_type': 'Wedding',
        'guest_count': 100,
        'location': 'Test Venue',
        'special_requests': 'Test special requests',
        'items': []
    }
