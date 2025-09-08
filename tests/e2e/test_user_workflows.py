"""
End-to-End Tests for Complete User Workflows
Tests entire user journeys from registration to booking completion
"""
import pytest
import json
import time

class TestCompleteUserJourney:
    """Test complete user workflows from start to finish"""
    
    def test_user_registration_to_booking_workflow(self, e2e_client, sample_user_data, sample_booking_data):
        """Test complete workflow: registration -> login -> browse -> book -> manage"""
        
        # Step 1: User Registration with file upload
        import io
        test_file = io.BytesIO(b"Mock ID file content for test")
        test_file.name = "test_id.jpg"
        
        register_response = e2e_client.post('/auth/register', 
                                          data=sample_user_data,
                                          content_type='multipart/form-data',
                                          files={'file': (test_file, 'test_id.jpg')})
        assert register_response.status_code == 201
        register_data = register_response.get_json()
        assert 'message' in register_data or 'success' in register_data
        
        # Step 2: User Login
        login_data = {
            'email': sample_user_data['email'],
            'password': sample_user_data['password']
        }
        login_response = e2e_client.post('/auth/login', json=login_data)
        assert login_response.status_code == 200
        login_result = login_response.get_json()
        assert 'token' in login_result
        
        headers = {'Authorization': f'Bearer {login_result["token"]}'}
        
        # Step 3: Browse Available Items
        items_response = e2e_client.get('/items')
        assert items_response.status_code == 200
        items_data = items_response.get_json()
        assert isinstance(items_data, list)
        
        # Step 4: Get Specific Item Details (if items exist)
        if items_data and len(items_data) > 0:
            first_item = items_data[0]
            item_detail_response = e2e_client.get(f'/items/{first_item["id"]}')
            assert item_detail_response.status_code == 200
            item_detail = item_detail_response.get_json()
            assert item_detail['id'] == first_item['id']
        
        # Step 5: Create a Booking
        booking_response = e2e_client.post('/bookings', json=sample_booking_data, headers=headers)
        assert booking_response.status_code == 201
        booking_result = booking_response.get_json()
        assert 'booking_id' in booking_result or '_id' in booking_result
        booking_id = booking_result.get('booking_id') or booking_result.get('_id')
        
        # Step 6: Retrieve User's Bookings
        user_bookings_response = e2e_client.get('/bookings/my', headers=headers)
        assert user_bookings_response.status_code == 200
        user_bookings = user_bookings_response.get_json()
        assert isinstance(user_bookings, (list, dict))
        
        # Handle both list response and paginated response
        bookings_list = user_bookings if isinstance(user_bookings, list) else user_bookings.get('bookings', [])
        
        # Verify the booking exists in user's bookings
        booking_found = any(
            booking.get('booking_id') == booking_id or booking.get('_id') == booking_id 
            for booking in bookings_list
        )
        assert booking_found, "Created booking not found in user's bookings"
        
        # Step 7: Get Specific Booking Details
        booking_detail_response = e2e_client.get(f'/bookings/{booking_id}', headers=headers)
        assert booking_detail_response.status_code == 200
        booking_detail = booking_detail_response.get_json()
        assert (booking_detail.get('booking_id') == booking_id or 
                booking_detail.get('_id') == booking_id)
        assert booking_detail['event_date'] == sample_booking_data['event_date']
    
    def test_guest_browsing_to_inquiry_workflow(self, e2e_client):
        """Test guest user workflow: browse items -> contact inquiry"""
        
        # Step 1: Guest Browse Items (no auth required)
        items_response = e2e_client.get('/items')
        assert items_response.status_code == 200
        items = items_response.get_json()
        assert isinstance(items, list)
        
        # Step 2: Guest View Item Details (if items exist)
        if items and len(items) > 0:
            item_id = items[0]['id']
            item_response = e2e_client.get(f'/items/{item_id}')
            assert item_response.status_code == 200
            item_detail = item_response.get_json()
            assert item_detail['id'] == item_id
        
        # Step 3: Guest Try to Access Protected Resource (should fail)
        bookings_response = e2e_client.get('/bookings/my')
        assert bookings_response.status_code == 401  # Unauthorized
    
    def test_booking_modification_workflow(self, e2e_client, auth_headers, sample_booking_data):
        """Test booking creation and modification workflow"""
        
        # Step 1: Create Initial Booking
        booking_response = e2e_client.post('/api/bookings', json=sample_booking_data, headers=auth_headers)
        assert booking_response.status_code == 201
        booking_result = booking_response.get_json()
        booking_id = booking_result['booking_id']
        
        # Step 2: Modify Booking Details
        updated_data = sample_booking_data.copy()
        updated_data['guest_count'] = 150
        updated_data['special_requests'] = 'Updated: Vegetarian + Gluten-free options'
        
        update_response = e2e_client.put(f'/api/bookings/{booking_id}', 
                                       json=updated_data, headers=auth_headers)
        assert update_response.status_code == 200
        
        # Step 3: Verify Changes
        verification_response = e2e_client.get(f'/api/bookings/{booking_id}', headers=auth_headers)
        assert verification_response.status_code == 200
        updated_booking = verification_response.get_json()
        assert updated_booking['guest_count'] == 150
        assert 'Updated:' in updated_booking['special_requests']
    
    def test_ai_assistant_integration_workflow(self, e2e_client, auth_headers):
        """Test AI assistant integration in user workflow"""
        
        # Step 1: Test AI Assistant Query
        ai_query = {
            'message': 'What wedding flowers do you recommend for a spring wedding?',
            'context': 'wedding planning'
        }
        
        ai_response = e2e_client.post('/api/ai/query', json=ai_query, headers=auth_headers)
        assert ai_response.status_code in [200, 400]  # 400 if quota exceeded
        
        if ai_response.status_code == 200:
            ai_result = ai_response.get_json()
            assert 'response' in ai_result
            assert isinstance(ai_result['response'], str)
        
        # Step 2: Test AI Assistant History
        history_response = e2e_client.get('/api/ai/history', headers=auth_headers)
        assert history_response.status_code == 200
        history = history_response.get_json()
        assert isinstance(history, list)


class TestMultiUserScenarios:
    """Test scenarios involving multiple users"""
    
    def test_concurrent_booking_scenario(self, e2e_client, sample_booking_data):
        """Test concurrent bookings by different users"""
        
        # Create two different users
        user1_data = {
            'full_name': 'User One',
            'email': 'user1@concurrent.test',
            'password': 'Pass123',
            'phone': '1111111111'
        }
        
        user2_data = {
            'full_name': 'User Two', 
            'email': 'user2@concurrent.test',
            'password': 'Pass123',
            'phone': '2222222222'
        }
        
        # Register both users
        e2e_client.post('/api/auth/register', json=user1_data)
        e2e_client.post('/api/auth/register', json=user2_data)
        
        # Login both users
        login1 = e2e_client.post('/api/auth/login', 
                               json={'email': user1_data['email'], 'password': user1_data['password']})
        login2 = e2e_client.post('/api/auth/login',
                               json={'email': user2_data['email'], 'password': user2_data['password']})
        
        headers1 = {'Authorization': f'Bearer {login1.get_json()["access_token"]}'}
        headers2 = {'Authorization': f'Bearer {login2.get_json()["access_token"]}'}
        
        # Both users create bookings
        booking1_data = sample_booking_data.copy()
        booking1_data['event_date'] = '2024-12-20'
        
        booking2_data = sample_booking_data.copy()
        booking2_data['event_date'] = '2024-12-21'
        
        response1 = e2e_client.post('/api/bookings', json=booking1_data, headers=headers1)
        response2 = e2e_client.post('/api/bookings', json=booking2_data, headers=headers2)
        
        assert response1.status_code == 201
        assert response2.status_code == 201
        
        # Verify each user can only see their own bookings
        user1_bookings = e2e_client.get('/api/bookings/my', headers=headers1)
        user2_bookings = e2e_client.get('/api/bookings/my', headers=headers2)
        
        user1_list = user1_bookings.get_json()
        user2_list = user2_bookings.get_json()
        
        assert len(user1_list) >= 1
        assert len(user2_list) >= 1
        
        # Ensure users can't access each other's specific bookings
        booking1_id = response1.get_json()['booking_id']
        booking2_id = response2.get_json()['booking_id']
        
        # User1 tries to access User2's booking (should fail)
        cross_access = e2e_client.get(f'/api/bookings/{booking2_id}', headers=headers1)
        assert cross_access.status_code in [403, 404]  # Forbidden or Not Found


class TestErrorHandlingWorkflows:
    """Test error scenarios and recovery workflows"""
    
    def test_invalid_registration_recovery(self, e2e_client):
        """Test user recovery from invalid registration attempts"""
        
        # Step 1: Attempt registration with invalid email
        invalid_data = {
            'full_name': 'Test User',
            'email': 'invalid-email',  # Invalid format
            'password': 'Pass123',
            'phone': '1234567890'
        }
        
        response = e2e_client.post('/api/auth/register', json=invalid_data)
        assert response.status_code == 422  # Validation error
        
        # Step 2: Correct the email and retry
        valid_data = invalid_data.copy()
        valid_data['email'] = 'corrected@example.com'
        
        retry_response = e2e_client.post('/api/auth/register', json=valid_data)
        assert retry_response.status_code == 201
    
    def test_booking_validation_workflow(self, e2e_client, auth_headers):
        """Test booking creation with validation errors"""
        
        # Step 1: Attempt booking with invalid date format
        invalid_booking = {
            'event_date': 'invalid-date',  # Invalid format
            'event_time': '18:00',
            'event_type': 'Wedding',
            'guest_count': 100
        }
        
        response = e2e_client.post('/api/bookings', json=invalid_booking, headers=auth_headers)
        assert response.status_code == 422  # Validation error
        
        # Step 2: Correct the data and retry
        valid_booking = invalid_booking.copy()
        valid_booking['event_date'] = '2024-12-25'
        
        retry_response = e2e_client.post('/api/bookings', json=valid_booking, headers=auth_headers)
        assert retry_response.status_code == 201
    
    def test_authentication_expiry_workflow(self, e2e_client, sample_user_data):
        """Test workflow when authentication token expires"""
        
        # Register and login user
        e2e_client.post('/api/auth/register', json=sample_user_data)
        login_response = e2e_client.post('/api/auth/login', 
                                       json={'email': sample_user_data['email'], 
                                           'password': sample_user_data['password']})
        
        token = login_response.get_json()['access_token']
        headers = {'Authorization': f'Bearer {token}'}
        
        # Test that valid token works
        bookings_response = e2e_client.get('/api/bookings/my', headers=headers)
        assert bookings_response.status_code == 200
        
        # Test with invalid token
        invalid_headers = {'Authorization': 'Bearer invalid_token'}
        invalid_response = e2e_client.get('/api/bookings/my', headers=invalid_headers)
        assert invalid_response.status_code == 422  # Invalid token format
        
        # Test with no token
        no_token_response = e2e_client.get('/api/bookings/my')
        assert no_token_response.status_code == 401  # Unauthorized
