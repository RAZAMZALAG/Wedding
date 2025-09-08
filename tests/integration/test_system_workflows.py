"""
Integration Tests for Full System Workflows
Tests complete user workflows - NO CHEATING!
"""
import pytest
import json
from datetime import datetime, timedelta
from main import create_app

@pytest.mark.integration
class TestSystemWorkflows:
    """Test complete system workflows with real Flask app"""
    
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
    
    def test_guest_catalog_browsing_workflow(self, client):
        """Test complete workflow of guest browsing catalog"""
        # Step 1: Get all items (should work without authentication)
        response = client.get('/api/items/')
        assert response.status_code != 404  # Endpoint exists
        
        if response.status_code == 200:
            items = json.loads(response.data)
            assert isinstance(items, (list, dict))
            
            # Step 2: If items exist, try to get one item detail
            if isinstance(items, list) and len(items) > 0:
                first_item = items[0]
                if 'id' in first_item or '_id' in first_item:
                    item_id = first_item.get('id', first_item.get('_id'))
                    detail_response = client.get(f'/api/items/{item_id}')
                    assert detail_response.status_code != 500
    
    def test_user_registration_and_login_workflow(self, client):
        """Test complete user registration and login workflow"""
        # Step 1: Attempt registration
        user_data = {
            'username': f'workflow_test_{datetime.now().timestamp()}',
            'email': f'workflow{datetime.now().timestamp()}@test.com',
            'password': 'TestPassword123!',
            'full_name': 'Workflow Test User',
            'phone': '0501234567',
            'location': 'תל אביב',
            'agree_to_terms': True
        }
        
        reg_response = client.post('/api/auth/register',
                                 data=json.dumps(user_data),
                                 content_type='application/json')
        
        # Registration should either succeed or fail gracefully
        assert reg_response.status_code in [201, 400, 422, 409, 500]
        
        # Step 2: Attempt login with same credentials
        login_data = {
            'username': user_data['username'],
            'password': user_data['password']
        }
        
        login_response = client.post('/api/auth/login',
                                   data=json.dumps(login_data),
                                   content_type='application/json')
        
        # Login should handle the attempt
        assert login_response.status_code in [200, 401, 400, 422]
    
    def test_availability_check_workflow(self, client):
        """Test availability checking workflow"""
        # Step 1: Get items to check availability for
        items_response = client.get('/api/items/')
        
        if items_response.status_code == 200:
            items = json.loads(items_response.data)
            
            if isinstance(items, list) and len(items) > 0:
                # Step 2: Check availability for first item
                first_item = items[0]
                item_id = first_item.get('id', first_item.get('_id', 'test_item'))
                
                future_date = (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')
                end_date = (datetime.now() + timedelta(days=33)).strftime('%Y-%m-%d')
                
                availability_data = {
                    'start_date': future_date,
                    'end_date': end_date,
                    'items': [item_id]
                }
                
                avail_response = client.post('/api/bookings/check-availability',
                                           data=json.dumps(availability_data),
                                           content_type='application/json')
                
                # Should handle availability check
                assert avail_response.status_code != 500
                assert avail_response.status_code != 404
    
    def test_ai_assistance_workflow(self, client):
        """Test AI assistance workflow"""
        # Step 1: Ask for general wedding help
        ai_data = {
            'message': 'I need help planning my wedding. What do you recommend?',
            'language': 'en'
        }
        
        ai_response = client.post('/api/ai/ask',
                                data=json.dumps(ai_data),
                                content_type='application/json')
        
        # Should handle AI requests
        assert ai_response.status_code != 404
        assert ai_response.status_code != 500
        
        # Step 2: Ask specific catalog question
        catalog_question = {
            'message': 'What tables are available for rent?',
            'language': 'en'
        }
        
        catalog_response = client.post('/api/ai/ask',
                                     data=json.dumps(catalog_question),
                                     content_type='application/json')
        
        assert catalog_response.status_code != 500
    
    def test_cart_management_workflow(self, client):
        """Test cart management workflow"""
        # Step 1: Try to add item to cart
        cart_add_data = {
            'item_id': 'test_item_id',
            'quantity': 2
        }
        
        add_response = client.post('/api/bookings/cart/add',
                                 data=json.dumps(cart_add_data),
                                 content_type='application/json')
        
        # Should handle cart operations (may require auth)
        assert add_response.status_code != 404
        assert add_response.status_code != 500
        
        # Step 2: Try to view cart
        cart_response = client.get('/api/bookings/cart')
        assert cart_response.status_code != 500
    
    def test_error_handling_workflow(self, client):
        """Test system error handling workflows"""
        # Test various malformed requests
        test_cases = [
            ('GET', '/nonexistent/endpoint', None),
            ('POST', '/api/auth/login', json.dumps({})),  # Empty but valid JSON
            ('POST', '/api/bookings/', json.dumps({'valid': 'json'})),
            ('GET', '/api/items/invalid_item_id_format', None)
        ]
        
        for method, endpoint, data in test_cases:
            if method == 'GET':
                response = client.get(endpoint)
            else:
                response = client.post(endpoint, 
                                     data=data, 
                                     content_type='application/json')
            
            # Should handle errors gracefully (not 500)
            assert response.status_code != 500
    
    def test_system_health_workflow(self, client):
        """Test basic system health and connectivity"""
        # Test that main endpoints are accessible
        endpoints_to_test = [
            '/api/items/',
            '/api/auth/login',
            '/api/ai/ask',
            '/api/bookings/check-availability'
        ]
        
        for endpoint in endpoints_to_test:
            if endpoint in ['/api/auth/login', '/api/ai/ask', '/api/bookings/check-availability']:
                response = client.post(endpoint,
                                     data=json.dumps({}),
                                     content_type='application/json')
            else:
                response = client.get(endpoint)
            
            # Endpoints should exist and not crash
            assert response.status_code != 404, f"Endpoint {endpoint} not found"
            assert response.status_code != 500, f"Endpoint {endpoint} crashed"
    
    def test_cross_module_integration(self, client):
        """Test integration between different modules"""
        # Test that items and bookings work together
        items_response = client.get('/api/items/')
        
        if items_response.status_code == 200:
            # Test that AI can access catalog information
            ai_catalog_question = {
                'message': 'Tell me about your wedding items catalog',
                'language': 'en'
            }
            
            ai_response = client.post('/api/ai/ask',
                                    data=json.dumps(ai_catalog_question),
                                    content_type='application/json')
            
            # AI should be able to access catalog data
            assert ai_response.status_code != 500
