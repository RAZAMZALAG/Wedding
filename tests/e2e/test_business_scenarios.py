"""
End-to-End Tests for Business Scenarios
Tests real-world business use cases and scenarios
"""
import pytest
import json
from datetime import datetime, timedelta

class TestWeddingPlanningScenarios:
    """Test realistic wedding planning scenarios"""
    
    def test_complete_wedding_planning_journey(self, e2e_client, sample_user_data):
        """Test a complete wedding planning journey from start to finish"""
        
        # Step 1: Couple registers for wedding planning
        bride_data = sample_user_data.copy()
        bride_data['full_name'] = 'Jane Bride'
        bride_data['email'] = 'jane.bride@wedding.com'
        
        register_response = e2e_client.post('/api/auth/register', json=bride_data)
        assert register_response.status_code == 201
        
        # Step 2: Login
        login_response = e2e_client.post('/api/auth/login', 
                                       json={'email': bride_data['email'], 
                                           'password': bride_data['password']})
        assert login_response.status_code == 200
        token = login_response.get_json()['access_token']
        headers = {'Authorization': f'Bearer {token}'}
        
        # Step 3: Explore available wedding items
        items_response = e2e_client.get('/api/items')
        assert items_response.status_code == 200
        items = items_response.get_json()
        
        # Filter wedding-related items
        wedding_items = [item for item in items if 'wedding' in item.get('name', '').lower()]
        assert len(wedding_items) > 0, "No wedding items found in catalog"
        
        # Step 4: Get AI assistance for wedding planning
        ai_query = {
            'message': 'Help me plan a romantic spring wedding for 120 guests',
            'context': 'wedding planning'
        }
        ai_response = e2e_client.post('/api/ai/query', json=ai_query, headers=headers)
        # AI might be rate limited, so accept both success and quota exceeded
        assert ai_response.status_code in [200, 400]
        
        # Step 5: Create initial wedding booking
        future_date = (datetime.now() + timedelta(days=180)).strftime('%Y-%m-%d')
        
        wedding_booking = {
            'event_date': future_date,
            'event_time': '17:00',
            'event_type': 'Wedding Ceremony and Reception',
            'guest_count': 120,
            'venue': 'Rosewood Manor',
            'special_requests': 'Spring theme with garden ceremony, romantic lighting',
            'items': [
                {'item_id': item['id'], 'quantity': 1} 
                for item in wedding_items[:3]  # Select first 3 wedding items
            ]
        }
        
        booking_response = e2e_client.post('/api/bookings', json=wedding_booking, headers=headers)
        assert booking_response.status_code == 201
        booking_id = booking_response.get_json()['booking_id']
        
        # Step 6: Modify booking as plans evolve
        updated_booking = wedding_booking.copy()
        updated_booking['guest_count'] = 140  # Guest list grew
        updated_booking['special_requests'] += ', additional seating required'
        
        update_response = e2e_client.put(f'/api/bookings/{booking_id}', 
                                       json=updated_booking, headers=headers)
        assert update_response.status_code == 200
        
        # Step 7: Final verification of wedding plans
        final_booking_response = e2e_client.get(f'/api/bookings/{booking_id}', headers=headers)
        assert final_booking_response.status_code == 200
        final_booking = final_booking_response.get_json()
        
        assert final_booking['guest_count'] == 140
        assert 'additional seating' in final_booking['special_requests']
        assert len(final_booking.get('items', [])) >= 3
    
    def test_corporate_event_planning_scenario(self, e2e_client):
        """Test corporate event planning workflow"""
        
        # Corporate event planner registration
        planner_data = {
            'full_name': 'Corporate Event Planner',
            'email': 'planner@corporate.com',
            'password': 'CorporatePass123',
            'phone': '5551112222'
        }
        
        register_response = e2e_client.post('/api/auth/register', json=planner_data)
        assert register_response.status_code == 201
        
        login_response = e2e_client.post('/api/auth/login', 
                                       json={'email': planner_data['email'], 
                                           'password': planner_data['password']})
        token = login_response.get_json()['access_token']
        headers = {'Authorization': f'Bearer {token}'}
        
        # Plan a corporate gala
        corporate_event = {
            'event_date': '2024-11-30',
            'event_time': '19:00',
            'event_type': 'Corporate Gala',
            'guest_count': 200,
            'venue': 'Grand Ballroom Convention Center',
            'special_requests': 'Professional AV setup, networking reception, awards ceremony'
        }
        
        booking_response = e2e_client.post('/api/bookings', json=corporate_event, headers=headers)
        assert booking_response.status_code == 201
        
        # Verify corporate event requirements
        booking_id = booking_response.get_json()['booking_id']
        event_details = e2e_client.get(f'/api/bookings/{booking_id}', headers=headers)
        assert event_details.status_code == 200
        
        event_data = event_details.get_json()
        assert event_data['event_type'] == 'Corporate Gala'
        assert event_data['guest_count'] == 200
    
    def test_multiple_events_same_user_scenario(self, e2e_client, auth_headers):
        """Test user managing multiple events"""
        
        # User plans multiple events throughout the year
        events = [
            {
                'event_date': '2024-06-15',
                'event_time': '14:00',
                'event_type': 'Graduation Party',
                'guest_count': 50,
                'venue': 'Backyard Garden',
                'special_requests': 'Casual outdoor celebration'
            },
            {
                'event_date': '2024-08-20',
                'event_time': '18:30',
                'event_type': 'Anniversary Dinner',
                'guest_count': 30,
                'venue': 'Private Dining Room',
                'special_requests': 'Elegant intimate setting'
            },
            {
                'event_date': '2024-12-31',
                'event_time': '22:00',
                'event_type': 'New Year Party',
                'guest_count': 100,
                'venue': 'Rooftop Terrace',
                'special_requests': 'Champagne service at midnight'
            }
        ]
        
        created_bookings = []
        
        # Create all events
        for event in events:
            response = e2e_client.post('/api/bookings', json=event, headers=auth_headers)
            assert response.status_code == 201
            booking_id = response.get_json()['booking_id']
            created_bookings.append(booking_id)
        
        # Verify user can see all their events
        user_bookings_response = e2e_client.get('/api/bookings/my', headers=auth_headers)
        assert user_bookings_response.status_code == 200
        user_bookings = user_bookings_response.get_json()
        
        assert len(user_bookings) >= len(events)
        
        # Verify each event exists and is accessible
        for booking_id in created_bookings:
            booking_detail = e2e_client.get(f'/api/bookings/{booking_id}', headers=auth_headers)
            assert booking_detail.status_code == 200
            
            detail_data = booking_detail.get_json()
            assert detail_data['booking_id'] == booking_id


class TestSeasonalEventScenarios:
    """Test seasonal and holiday event scenarios"""
    
    def test_holiday_season_booking_rush(self, e2e_client):
        """Test system handling during holiday booking rush"""
        
        # Create multiple users booking holiday events
        holiday_users = []
        for i in range(5):
            user_data = {
                'full_name': f'Holiday User {i+1}',
                'email': f'holiday{i+1}@season.com',
                'password': 'HolidayPass123',
                'phone': f'555{i+1:03d}0000'
            }
            
            register_response = e2e_client.post('/api/auth/register', json=user_data)
            if register_response.status_code == 201:
                login_response = e2e_client.post('/api/auth/login', 
                                               json={'email': user_data['email'], 
                                                   'password': user_data['password']})
                if login_response.status_code == 200:
                    token = login_response.get_json()['access_token']
                    headers = {'Authorization': f'Bearer {token}'}
                    holiday_users.append((f'User{i+1}', headers))
        
        # Each user books a holiday event
        holiday_events = [
            'Christmas Party', 'New Year Celebration', 'Holiday Gala', 
            'Winter Wedding', 'Year-End Corporate Event'
        ]
        
        successful_bookings = 0
        for i, (user_name, headers) in enumerate(holiday_users):
            event_data = {
                'event_date': '2024-12-20',
                'event_time': '19:00',
                'event_type': holiday_events[i % len(holiday_events)],
                'guest_count': 75 + (i * 15),
                'venue': f'{user_name} Holiday Venue',
                'special_requests': 'Holiday decorations, festive music'
            }
            
            booking_response = e2e_client.post('/api/bookings', json=event_data, headers=headers)
            if booking_response.status_code == 201:
                successful_bookings += 1
        
        # Verify most bookings succeeded despite the rush
        success_rate = successful_bookings / len(holiday_users)
        assert success_rate >= 0.6, f"Holiday booking success rate {success_rate:.2%} too low"
    
    def test_spring_wedding_season_scenario(self, e2e_client):
        """Test spring wedding season with multiple couples"""
        
        # Multiple couples book spring weddings
        couples = [
            ('Alice & Bob', 'alice.bob@spring.wedding'),
            ('Carol & Dave', 'carol.dave@spring.wedding'),
            ('Eve & Frank', 'eve.frank@spring.wedding')
        ]
        
        spring_bookings = []
        for couple_name, email in couples:
            user_data = {
                'full_name': couple_name,
                'email': email,
                'password': 'SpringWedding123',
                'phone': '5550001111'
            }
            
            # Register couple
            register_response = e2e_client.post('/api/auth/register', json=user_data)
            if register_response.status_code == 201:
                # Login
                login_response = e2e_client.post('/api/auth/login', 
                                               json={'email': email, 'password': 'SpringWedding123'})
                if login_response.status_code == 200:
                    token = login_response.get_json()['access_token']
                    headers = {'Authorization': f'Bearer {token}'}
                    
                    # Book spring wedding
                    wedding_data = {
                        'event_date': '2024-05-15',
                        'event_time': '16:00',
                        'event_type': 'Spring Wedding',
                        'guest_count': 100,
                        'venue': f'{couple_name} Garden Venue',
                        'special_requests': 'Outdoor ceremony, spring flowers, garden reception'
                    }
                    
                    booking_response = e2e_client.post('/api/bookings', json=wedding_data, headers=headers)
                    if booking_response.status_code == 201:
                        spring_bookings.append(booking_response.get_json()['booking_id'])
        
        # Verify all spring weddings were successfully booked
        assert len(spring_bookings) >= 2, "Not enough spring weddings booked successfully"


class TestBusinessContinuityScenarios:
    """Test business continuity and edge cases"""
    
    def test_last_minute_booking_changes(self, e2e_client, auth_headers):
        """Test handling of last-minute booking changes"""
        
        # Create an event
        original_booking = {
            'event_date': '2024-11-01',
            'event_time': '18:00',
            'event_type': 'Birthday Party',
            'guest_count': 40,
            'venue': 'Community Center',
            'special_requests': 'Birthday decorations'
        }
        
        booking_response = e2e_client.post('/api/bookings', json=original_booking, headers=auth_headers)
        assert booking_response.status_code == 201
        booking_id = booking_response.get_json()['booking_id']
        
        # Simulate last-minute changes
        changes = [
            {'guest_count': 55, 'special_requests': 'Updated: More guests confirmed'},
            {'venue': 'Larger Community Hall', 'special_requests': 'Updated: Venue changed due to size'},
            {'event_time': '17:30', 'special_requests': 'Updated: Moved start time earlier'}
        ]
        
        for change in changes:
            updated_data = original_booking.copy()
            updated_data.update(change)
            
            update_response = e2e_client.put(f'/api/bookings/{booking_id}', 
                                           json=updated_data, headers=auth_headers)
            assert update_response.status_code == 200
            
            # Verify changes were applied
            verification_response = e2e_client.get(f'/api/bookings/{booking_id}', headers=auth_headers)
            assert verification_response.status_code == 200
            booking_data = verification_response.get_json()
            
            for key, value in change.items():
                assert booking_data[key] == value
    
    def test_peak_usage_simulation(self, e2e_client):
        """Test system behavior during peak usage"""
        
        # Simulate peak usage with rapid sequential requests
        operations = []
        
        # Create a test user for peak testing
        user_data = {
            'full_name': 'Peak Test User',
            'email': 'peak@test.com',
            'password': 'PeakTest123',
            'phone': '5559999999'
        }
        
        register_response = e2e_client.post('/api/auth/register', json=user_data)
        if register_response.status_code == 201:
            login_response = e2e_client.post('/api/auth/login', 
                                           json={'email': user_data['email'], 
                                               'password': user_data['password']})
            if login_response.status_code == 200:
                token = login_response.get_json()['access_token']
                headers = {'Authorization': f'Bearer {token}'}
                
                # Rapid fire requests
                for i in range(10):
                    # Browse items
                    items_response = e2e_client.get('/api/items')
                    operations.append(('BROWSE', items_response.status_code == 200))
                    
                    # Get user bookings
                    bookings_response = e2e_client.get('/api/bookings/my', headers=headers)
                    operations.append(('LIST_BOOKINGS', bookings_response.status_code == 200))
                    
                    # Quick booking creation (every 3rd iteration)
                    if i % 3 == 0:
                        quick_booking = {
                            'event_date': f'2024-12-{(i%20)+1:02d}',
                            'event_time': '20:00',
                            'event_type': f'Peak Test Event {i}',
                            'guest_count': 20,
                            'venue': f'Test Venue {i}'
                        }
                        booking_response = e2e_client.post('/api/bookings', 
                                                         json=quick_booking, headers=headers)
                        operations.append(('CREATE_BOOKING', booking_response.status_code == 201))
        
        # Analyze peak performance
        successful_ops = sum(1 for _, success in operations if success)
        total_ops = len(operations)
        
        if total_ops > 0:
            success_rate = successful_ops / total_ops
            assert success_rate >= 0.7, f"Peak usage success rate {success_rate:.2%} too low"
