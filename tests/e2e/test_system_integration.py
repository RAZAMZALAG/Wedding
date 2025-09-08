"""
End-to-End Tests for System Integration
Tests cross-component functionality and system-wide features
"""
import pytest
import json
import time

class TestSystemIntegration:
    """Test system-wide integration scenarios"""
    
    def test_full_catalog_to_booking_integration(self, e2e_client, auth_headers):
        """Test complete catalog browsing to booking creation integration"""
        
        # Step 1: Get all available items
        catalog_response = e2e_client.get('/api/items')
        assert catalog_response.status_code == 200
        catalog = catalog_response.get_json()
        assert isinstance(catalog, list)
        assert len(catalog) > 0
        
        # Step 2: Select items for booking
        selected_items = []
        for item in catalog[:3]:  # Select first 3 items
            item_detail_response = e2e_client.get(f'/api/items/{item["id"]}')
            assert item_detail_response.status_code == 200
            item_detail = item_detail_response.get_json()
            
            selected_items.append({
                'item_id': item['id'],
                'quantity': 1
            })
        
        # Step 3: Create booking with selected items
        booking_data = {
            'event_date': '2024-12-30',
            'event_time': '19:00',
            'event_type': 'Wedding Reception',
            'guest_count': 80,
            'venue': 'Seaside Resort',
            'special_requests': 'Ocean view setup',
            'items': selected_items
        }
        
        booking_response = e2e_client.post('/api/bookings', json=booking_data, headers=auth_headers)
        assert booking_response.status_code == 201
        booking_result = booking_response.get_json()
        assert 'booking_id' in booking_result
        
        # Step 4: Verify booking contains all selected items
        booking_id = booking_result['booking_id']
        booking_detail_response = e2e_client.get(f'/api/bookings/{booking_id}', headers=auth_headers)
        assert booking_detail_response.status_code == 200
        booking_detail = booking_detail_response.get_json()
        
        # Verify all items are in the booking
        booking_items = booking_detail.get('items', [])
        assert len(booking_items) == len(selected_items)
        for selected_item in selected_items:
            item_found = any(
                booking_item['item_id'] == selected_item['item_id'] 
                for booking_item in booking_items
            )
            assert item_found, f"Item {selected_item['item_id']} not found in booking"
    
    def test_user_authentication_across_all_endpoints(self, e2e_client):
        """Test authentication requirements across all protected endpoints"""
        
        # Create a test user
        user_data = {
            'full_name': 'Auth Test User',
            'email': 'authtest@example.com',
            'password': 'AuthTest123',
            'phone': '5556667777'
        }
        
        # Register and login
        register_response = e2e_client.post('/api/auth/register', json=user_data)
        assert register_response.status_code == 201
        
        login_response = e2e_client.post('/api/auth/login', 
                                       json={'email': user_data['email'], 
                                           'password': user_data['password']})
        assert login_response.status_code == 200
        token = login_response.get_json()['access_token']
        headers = {'Authorization': f'Bearer {token}'}
        
        # Test protected endpoints with valid authentication
        protected_endpoints = [
            ('/api/bookings/my', 'GET'),
            ('/api/ai/history', 'GET'),
        ]
        
        for endpoint, method in protected_endpoints:
            if method == 'GET':
                response = e2e_client.get(endpoint, headers=headers)
            elif method == 'POST':
                response = e2e_client.post(endpoint, json={}, headers=headers)
            
            assert response.status_code != 401, f"Authenticated request to {endpoint} failed"
        
        # Test same endpoints without authentication (should fail)
        for endpoint, method in protected_endpoints:
            if method == 'GET':
                response = e2e_client.get(endpoint)
            elif method == 'POST':
                response = e2e_client.post(endpoint, json={})
            
            assert response.status_code == 401, f"Unauthenticated request to {endpoint} should fail"
    
    def test_data_consistency_across_operations(self, e2e_client, auth_headers):
        """Test data consistency when performing multiple operations"""
        
        # Create a booking
        booking_data = {
            'event_date': '2024-11-15',
            'event_time': '16:00',
            'event_type': 'Anniversary',
            'guest_count': 50,
            'venue': 'Garden Pavilion',
            'special_requests': 'Romantic setup'
        }
        
        booking_response = e2e_client.post('/api/bookings', json=booking_data, headers=auth_headers)
        assert booking_response.status_code == 201
        booking_id = booking_response.get_json()['booking_id']
        
        # Retrieve the booking multiple times to ensure consistency
        for _ in range(3):
            detail_response = e2e_client.get(f'/api/bookings/{booking_id}', headers=auth_headers)
            assert detail_response.status_code == 200
            booking_detail = detail_response.get_json()
            
            # Verify data consistency
            assert booking_detail['event_date'] == booking_data['event_date']
            assert booking_detail['event_time'] == booking_data['event_time']
            assert booking_detail['guest_count'] == booking_data['guest_count']
            assert booking_detail['venue'] == booking_data['venue']
        
        # Update the booking
        updated_data = booking_data.copy()
        updated_data['guest_count'] = 75
        updated_data['special_requests'] = 'Updated: Romantic setup with extra lighting'
        
        update_response = e2e_client.put(f'/api/bookings/{booking_id}', 
                                       json=updated_data, headers=auth_headers)
        assert update_response.status_code == 200
        
        # Verify update consistency
        updated_detail_response = e2e_client.get(f'/api/bookings/{booking_id}', headers=auth_headers)
        assert updated_detail_response.status_code == 200
        updated_detail = updated_detail_response.get_json()
        assert updated_detail['guest_count'] == 75
        assert 'Updated:' in updated_detail['special_requests']
    
    def test_ai_assistant_system_integration(self, e2e_client, auth_headers):
        """Test AI assistant integration with the rest of the system"""
        
        # Test AI assistant with booking context
        ai_query = {
            'message': 'I need help planning a winter wedding for 100 guests',
            'context': 'wedding planning'
        }
        
        ai_response = e2e_client.post('/api/ai/query', json=ai_query, headers=auth_headers)
        assert ai_response.status_code in [200, 400]  # 400 if quota exceeded
        
        if ai_response.status_code == 200:
            ai_result = ai_response.get_json()
            assert 'response' in ai_result
            assert isinstance(ai_result['response'], str)
            assert len(ai_result['response']) > 0
        
        # Test AI history retrieval
        history_response = e2e_client.get('/api/ai/history', headers=auth_headers)
        assert history_response.status_code == 200
        history = history_response.get_json()
        assert isinstance(history, list)


class TestSystemReliability:
    """Test system reliability and error recovery"""
    
    def test_database_connection_resilience(self, e2e_client, auth_headers):
        """Test system behavior with database operations"""
        
        # Perform multiple database operations in sequence
        operations = []
        
        # 1. Create multiple bookings
        for i in range(3):
            booking_data = {
                'event_date': f'2024-12-{10+i:02d}',
                'event_time': '15:00',
                'event_type': f'Event {i+1}',
                'guest_count': 25 + (i * 10),
                'venue': f'Venue {i+1}'
            }
            
            response = e2e_client.post('/api/bookings', json=booking_data, headers=auth_headers)
            operations.append(('CREATE', response.status_code == 201))
            
            if response.status_code == 201:
                booking_id = response.get_json()['booking_id']
                
                # 2. Read the booking
                read_response = e2e_client.get(f'/api/bookings/{booking_id}', headers=auth_headers)
                operations.append(('READ', read_response.status_code == 200))
                
                # 3. Update the booking
                updated_data = booking_data.copy()
                updated_data['special_requests'] = f'Updated request {i+1}'
                update_response = e2e_client.put(f'/api/bookings/{booking_id}', 
                                               json=updated_data, headers=auth_headers)
                operations.append(('UPDATE', update_response.status_code == 200))
        
        # Verify most operations succeeded
        successful_operations = sum(1 for _, success in operations if success)
        total_operations = len(operations)
        success_rate = successful_operations / total_operations
        
        assert success_rate >= 0.8, f"Success rate {success_rate:.2%} too low"
    
    def test_concurrent_user_operations(self, e2e_client):
        """Test system behavior with concurrent user operations"""
        
        # Create multiple users
        users = []
        for i in range(3):
            user_data = {
                'full_name': f'Concurrent User {i+1}',
                'email': f'concurrent{i+1}@test.com',
                'password': 'ConcurrentTest123',
                'phone': f'555000000{i+1}'
            }
            
            # Register user
            register_response = e2e_client.post('/api/auth/register', json=user_data)
            if register_response.status_code == 201:
                # Login user
                login_response = e2e_client.post('/api/auth/login', 
                                               json={'email': user_data['email'], 
                                                   'password': user_data['password']})
                if login_response.status_code == 200:
                    token = login_response.get_json()['access_token']
                    headers = {'Authorization': f'Bearer {token}'}
                    users.append((f'User{i+1}', headers))
        
        # Each user performs operations
        all_bookings = []
        for user_name, headers in users:
            booking_data = {
                'event_date': '2024-12-15',
                'event_time': '18:00',
                'event_type': f'{user_name} Event',
                'guest_count': 60,
                'venue': f'{user_name} Venue'
            }
            
            booking_response = e2e_client.post('/api/bookings', json=booking_data, headers=headers)
            if booking_response.status_code == 201:
                booking_id = booking_response.get_json()['booking_id']
                all_bookings.append((user_name, booking_id, headers))
        
        # Verify each user can access their own bookings
        for user_name, booking_id, headers in all_bookings:
            user_bookings_response = e2e_client.get('/api/bookings/my', headers=headers)
            assert user_bookings_response.status_code == 200
            
            user_bookings = user_bookings_response.get_json()
            user_booking_ids = [booking['booking_id'] for booking in user_bookings]
            assert booking_id in user_booking_ids
    
    def test_api_endpoint_availability(self, e2e_client):
        """Test that all API endpoints are available and respond appropriately"""
        
        # Test public endpoints (no auth required)
        public_endpoints = [
            '/api/items',
        ]
        
        for endpoint in public_endpoints:
            response = e2e_client.get(endpoint)
            assert response.status_code == 200, f"Public endpoint {endpoint} not available"
        
        # Test auth endpoints
        auth_endpoints = [
            '/api/auth/register',
            '/api/auth/login'
        ]
        
        for endpoint in auth_endpoints:
            # Test with empty POST (should return validation error, not 404)
            response = e2e_client.post(endpoint, json={})
            assert response.status_code != 404, f"Auth endpoint {endpoint} not found"
            assert response.status_code in [400, 422], f"Auth endpoint {endpoint} not handling requests"
