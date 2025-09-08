"""
Integration Tests for Bookings API
Tests real booking endpoints - NO CHEATING!
"""
import pytest
import json
from datetime import datetime, timedelta
from main import create_app

@pytest.mark.integration
class TestBookingsAPI:
    """Test booking endpoints with real Flask app"""
    
    @pytest.fixture(scope="class")
    def app(self):
        """Create test Flask application"""
        app = create_app()
        app.config['TESTING'] = True
        app.config['JWT_SECRET_KEY'] = 'test_jwt_secret_for_integration'
        return app
    
    @pytest.fixture(scope="class")
    def client(self, app):
        """Create test client"""
        return app.test_client()
    
    def test_bookings_endpoint_exists(self, client):
        """Test that bookings endpoint exists"""
        response = client.get('/api/bookings/')
        # Should not be 404 (endpoint exists), likely 401 (needs auth)
        assert response.status_code != 404
    
    def test_bookings_requires_authentication(self, client):
        """Test that bookings require authentication"""
        response = client.get('/api/bookings/')
        # Should require authentication
        assert response.status_code in [401, 422]
    
    def test_check_availability_endpoint(self, client):
        """Test availability checking endpoint"""
        today = datetime.now()
        start_date = (today + timedelta(days=7)).strftime('%Y-%m-%d')
        end_date = (today + timedelta(days=10)).strftime('%Y-%m-%d')
        
        response = client.post('/api/bookings/check-availability',
                             data=json.dumps({
                                 'start_date': start_date,
                                 'end_date': end_date,
                                 'items': ['item1', 'item2']
                             }),
                             content_type='application/json')
        
        # Should handle availability checking (may require auth)
        assert response.status_code != 500
        assert response.status_code != 404  # Endpoint should exist
    
    def test_check_availability_invalid_dates(self, client):
        """Test availability check with invalid dates"""
        response = client.post('/api/bookings/check-availability',
                             data=json.dumps({
                                 'start_date': 'invalid-date',
                                 'end_date': '2025-12-01',
                                 'items': []
                             }),
                             content_type='application/json')
        
        # Should handle invalid dates gracefully
        assert response.status_code in [400, 422, 401]  # Bad request or needs auth
    
    def test_check_availability_past_dates(self, client):
        """Test availability check with past dates"""
        yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
        today = datetime.now().strftime('%Y-%m-%d')
        
        response = client.post('/api/bookings/check-availability',
                             data=json.dumps({
                                 'start_date': yesterday,
                                 'end_date': today,
                                 'items': []
                             }),
                             content_type='application/json')
        
        # Should handle past dates (may reject or require auth)
        assert response.status_code != 500
    
    def test_cart_operations_endpoint(self, client):
        """Test cart operations endpoints"""
        # Test add to cart
        response = client.post('/api/bookings/cart/add',
                             data=json.dumps({
                                 'item_id': 'test_item',
                                 'quantity': 1
                             }),
                             content_type='application/json')
        
        # Should handle cart operations (likely requires auth)
        assert response.status_code != 404  # Endpoint should exist
        assert response.status_code != 500  # Should not crash
    
    def test_get_available_date_ranges(self, client):
        """Test getting available date ranges for items"""
        response = client.get('/api/bookings/available-date-ranges?item_id=test_item')
        
        # Should handle date range queries
        assert response.status_code != 404
        assert response.status_code != 500
    
    def test_booking_creation_without_auth(self, client):
        """Test creating booking without authentication"""
        booking_data = {
            'start_date': '2025-12-01',
            'end_date': '2025-12-03',
            'items': [{'item_id': 'test_item', 'quantity': 1}],
            'event_type': 'wedding',
            'guest_count': 100
        }
        
        response = client.post('/api/bookings/',
                             data=json.dumps(booking_data),
                             content_type='application/json')
        
        # Should require authentication
        assert response.status_code in [401, 422]
    
    def test_lock_items_functionality(self, client):
        """Test temporary item locking functionality"""
        lock_data = {
            'items': [{'item_id': 'test_item', 'quantity': 1}],
            'start_date': '2025-12-01',
            'end_date': '2025-12-03'
        }
        
        response = client.post('/api/bookings/lock-items',
                             data=json.dumps(lock_data),
                             content_type='application/json')
        
        # Should handle item locking (may require auth)
        assert response.status_code != 404
        assert response.status_code != 500
    
    def test_booking_endpoints_handle_json(self, client):
        """Test that booking endpoints properly handle JSON"""
        endpoints = [
            '/api/bookings/check-availability',
            '/api/bookings/cart/add',
            '/api/bookings/lock-items'
        ]
        
        for endpoint in endpoints:
            response = client.post(endpoint,
                                 data='invalid json',
                                 content_type='application/json')
            
            # Should handle malformed JSON gracefully
            assert response.status_code != 500
            assert response.status_code in [400, 401, 422]
    
    def test_booking_status_updates(self, client):
        """Test booking status update functionality"""
        # Try to update a booking status using correct endpoint format
        response = client.put('/api/bookings/test_booking_id/status/confirmed',
                            content_type='application/json')
        
        # Should handle status updates (likely requires admin auth)
        assert response.status_code != 500
        assert response.status_code != 404
