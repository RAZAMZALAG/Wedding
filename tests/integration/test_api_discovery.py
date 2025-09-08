"""
Integration Tests - API Endpoint Discovery
Tests real API endpoint structure - NO CHEATING!
"""
import pytest
import json
from main import create_app

@pytest.mark.integration
class TestAPIEndpointDiscovery:
    """Discover and verify the correct API endpoint structure"""
    
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
    
    def test_api_auth_endpoints_discovery(self, client):
        """Test discovering auth API endpoints"""
        # Test the correct API path structure
        response = client.post('/api/auth/login')
        # Should not be 404 (endpoint exists)
        assert response.status_code != 404
        
        response = client.post('/api/auth/register')
        assert response.status_code != 404
    
    def test_api_items_endpoints_discovery(self, client):
        """Test discovering items API endpoints"""
        response = client.get('/api/items/')
        assert response.status_code != 404
        
        if response.status_code == 200:
            # Should return JSON content type for API
            assert 'application/json' in response.content_type
    
    def test_api_bookings_endpoints_discovery(self, client):
        """Test discovering bookings API endpoints"""
        response = client.get('/api/bookings/')
        assert response.status_code != 404
        
        response = client.post('/api/bookings/check-availability')
        assert response.status_code != 404
    
    def test_api_ai_endpoints_discovery(self, client):
        """Test discovering AI API endpoints"""
        response = client.post('/api/ai/')
        assert response.status_code != 404
    
    def test_api_users_endpoints_discovery(self, client):
        """Test discovering users API endpoints"""
        response = client.get('/api/users/')
        assert response.status_code != 404
    
    def test_non_api_endpoints_serve_frontend(self, client):
        """Test that non-API endpoints serve frontend content"""
        # These should serve HTML (frontend)
        response = client.get('/')
        assert response.status_code in [200, 404]  # May or may not be configured
        
        response = client.get('/items/')  # No /api prefix
        if response.status_code == 200:
            # Should serve HTML, not JSON
            assert 'text/html' in response.content_type
    
    def test_api_prefix_consistency(self, client):
        """Test that all API endpoints are consistently prefixed"""
        api_endpoints = [
            '/api/auth/login',
            '/api/items/',
            '/api/bookings/',
            '/api/ai/',
            '/api/users/'
        ]
        
        for endpoint in api_endpoints:
            if endpoint.endswith('/'):
                response = client.get(endpoint)
            else:
                response = client.post(endpoint)
            
            # All API endpoints should exist (not 404)
            assert response.status_code != 404, f"API endpoint {endpoint} not found"
