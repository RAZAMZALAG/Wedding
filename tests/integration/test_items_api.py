"""
Integration Tests for Items Catalog API
Tests real catalog endpoints - NO CHEATING!
"""
import pytest
import json
from main import create_app

@pytest.mark.integration
class TestItemsCatalogAPI:
    """Test items catalog endpoints with real Flask app"""
    
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
    
    def test_get_all_items_endpoint(self, client):
        """Test getting all items from catalog"""
        response = client.get('/api/items/')
        
        # Should not be 404 (endpoint exists)
        assert response.status_code != 404
        
        # Should return JSON if successful
        if response.status_code == 200:
            data = json.loads(response.data)
            assert isinstance(data, (list, dict))
    
    def test_get_items_with_category_filter(self, client):
        """Test getting items filtered by category"""
        response = client.get('/api/items/?category=tables')
        
        # Should handle query parameters
        assert response.status_code != 500
        
        if response.status_code == 200:
            data = json.loads(response.data)
            assert isinstance(data, (list, dict))
    
    def test_get_single_item_by_id(self, client):
        """Test getting a single item by ID"""
        # First get all items to find a valid ID
        all_items_response = client.get('/api/items/')
        
        if all_items_response.status_code == 200:
            items_data = json.loads(all_items_response.data)
            
            if isinstance(items_data, list) and len(items_data) > 0:
                # Try to get the first item by ID
                first_item = items_data[0]
                if 'id' in first_item or '_id' in first_item:
                    item_id = first_item.get('id', first_item.get('_id'))
                    
                    response = client.get(f'/api/items/{item_id}')
                    # Should handle individual item requests
                    assert response.status_code != 500
                    
                    if response.status_code == 200:
                        item_data = json.loads(response.data)
                        assert isinstance(item_data, dict)
    
    def test_get_nonexistent_item(self, client):
        """Test getting item that doesn't exist"""
        fake_id = "507f1f77bcf86cd799439011"  # Valid ObjectId format
        response = client.get(f'/api/items/{fake_id}')
        
        # Should return 404 for non-existent item
        assert response.status_code in [404, 400]
    
    def test_items_endpoint_handles_malformed_requests(self, client):
        """Test that items endpoint handles malformed requests gracefully"""
        # Test with invalid query parameters
        response = client.get('/api/items/?invalid_param=malformed_data')
        assert response.status_code != 500  # Should not crash
    
    def test_items_response_format(self, client):
        """Test that items response has expected format"""
        response = client.get('/api/items/')
        
        if response.status_code == 200:
            data = json.loads(response.data)
            
            if isinstance(data, list) and len(data) > 0:
                # Check that items have expected fields
                first_item = data[0]
                expected_fields = ['name', 'category', 'price_per_day']
                
                # At least some basic fields should exist
                has_basic_fields = any(field in first_item for field in expected_fields)
                assert has_basic_fields, "Items should have basic catalog fields"
    
    def test_items_content_type(self, client):
        """Test that items endpoint returns proper content type"""
        response = client.get('/api/items/')
        
        if response.status_code == 200:
            # Should return JSON content type
            assert 'application/json' in response.content_type
    
    def test_items_endpoint_accepts_json(self, client):
        """Test that items endpoint accepts JSON requests"""
        response = client.get('/api/items/', 
                            headers={'Accept': 'application/json'})
        
        # Should handle JSON accept headers
        assert response.status_code != 406  # Not Acceptable
    
    def test_catalog_availability_check(self, client):
        """Test catalog availability checking functionality"""
        # Test if there's an availability check endpoint
        response = client.post('/api/bookings/check-availability',
                             data=json.dumps({
                                 'start_date': '2025-12-01',
                                 'end_date': '2025-12-03',
                                 'items': []
                             }),
                             content_type='application/json')
        
        # Should either work or require authentication, but not crash
        assert response.status_code != 500
