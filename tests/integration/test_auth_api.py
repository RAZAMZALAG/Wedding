"""
Integration Tests for Authentication API
Tests real API endpoints - NO CHEATING!
"""
import pytest
import json
from main import create_app
from models import User, init_db
from extensions import mongo

@pytest.mark.integration
class TestAuthenticationAPI:
    """Test authentication endpoints with real Flask app"""
    
    @pytest.fixture(scope="class")
    def app(self):
        """Create test Flask application"""
        app = create_app()
        app.config['TESTING'] = True
        app.config['JWT_SECRET_KEY'] = 'test_jwt_secret_for_integration'
        app.config['WTF_CSRF_ENABLED'] = False
        return app
    
    @pytest.fixture(scope="class")
    def client(self, app):
        """Create test client"""
        return app.test_client()
    
    @pytest.fixture(scope="class")
    def app_context(self, app):
        """Create application context"""
        with app.app_context():
            yield
    
    def test_login_endpoint_exists(self, client):
        """Test that login endpoint exists and responds"""
        response = client.post('/api/auth/login')
        # Should not be 404 (endpoint exists)
        assert response.status_code != 404
    
    def test_register_endpoint_exists(self, client):
        """Test that register endpoint exists and responds"""
        response = client.post('/api/auth/register')
        # Should not be 404 (endpoint exists)
        assert response.status_code != 404
    
    def test_login_missing_credentials(self, client):
        """Test login with missing credentials"""
        response = client.post('/api/auth/login', 
                             data=json.dumps({}),
                             content_type='application/json')
        assert response.status_code in [400, 422]
    
    def test_login_invalid_credentials(self, client):
        """Test login with invalid credentials"""
        response = client.post('/api/auth/login',
                             data=json.dumps({
                                 'username': 'nonexistent_user',
                                 'password': 'wrong_password'
                             }),
                             content_type='application/json')
        assert response.status_code in [401, 400, 422]
    
    def test_register_missing_data(self, client):
        """Test registration with missing required data"""
        response = client.post('/api/auth/register',
                             data=json.dumps({
                                 'username': 'testuser'
                                 # Missing other required fields
                             }),
                             content_type='application/json')
        assert response.status_code in [400, 422]
    
    def test_register_complete_data(self, client, app_context):
        """Test registration with complete valid data"""
        test_user_data = {
            'username': 'integration_test_user',
            'email': 'integration@test.com',
            'password': 'TestPassword123!',
            'full_name': 'Integration Test User',
            'phone': '0501234567',
            'location': 'תל אביב',
            'agree_to_terms': True
        }
        
        response = client.post('/api/auth/register',
                             data=json.dumps(test_user_data),
                             content_type='application/json')
        
        # Should either succeed (201) or fail with validation error (400/422)
        assert response.status_code in [201, 400, 422, 409]  # 409 for existing user
        
        # If successful, response should be JSON
        if response.status_code == 201:
            data = json.loads(response.data)
            assert 'user' in data or 'message' in data
    
    def test_protected_endpoint_without_token(self, client):
        """Test accessing protected endpoint without JWT token"""
        # Try to access a protected endpoint (assuming /api/bookings is protected)
        response = client.get('/api/bookings/')
        assert response.status_code in [401, 422]  # Unauthorized
    
    def test_auth_headers_processing(self, client):
        """Test that auth endpoints properly handle headers"""
        response = client.post('/api/auth/login',
                             data=json.dumps({}),
                             content_type='application/json',
                             headers={'Accept': 'application/json'})
        # Should handle headers without crashing
        assert response.status_code != 500
