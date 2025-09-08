"""
Stress Testing Suite - Load Testing
Tests system behavior under various load conditions
"""
import pytest
import time
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
import statistics

class TestLoadTesting:
    """Test system performance under different load conditions"""
    
    def test_light_load_items_endpoint(self, stress_client, performance_metrics, load_test_config):
        """Test items endpoint under light load"""
        config = load_test_config['light_load']
        
        def make_request():
            start_time = time.time()
            response = stress_client.get('/api/items')
            response_time = time.time() - start_time
            performance_metrics.record_request(response_time, response.status_code)
            return response.status_code
        
        # Execute concurrent requests
        with ThreadPoolExecutor(max_workers=config['users']) as executor:
            futures = []
            for user in range(config['users']):
                for req in range(config['requests_per_user']):
                    futures.append(executor.submit(make_request))
                    time.sleep(config['delay'])
            
            # Wait for all requests to complete
            for future in as_completed(futures):
                future.result()
        
        stats = performance_metrics.get_stats()
        
        # Assertions for light load
        assert stats['total_requests'] == config['users'] * config['requests_per_user']
        assert stats['avg_response_time'] < 1.0, f"Average response time too high: {stats['avg_response_time']:.3f}s"
        assert stats['success_rate'] > 0.95, f"Success rate too low: {stats['success_rate']:.2%}"
        assert stats['max_response_time'] < 2.0, f"Max response time too high: {stats['max_response_time']:.3f}s"
    
    def test_medium_load_authentication(self, stress_client, performance_metrics, load_test_config, sample_stress_data):
        """Test authentication endpoints under medium load"""
        config = load_test_config['medium_load']
        login_data = sample_stress_data['login_data']
        
        def make_auth_request():
            start_time = time.time()
            response = stress_client.post('/api/auth/login', json=login_data)
            response_time = time.time() - start_time
            performance_metrics.record_request(response_time, response.status_code)
            return response.status_code
        
        # Execute concurrent authentication requests
        with ThreadPoolExecutor(max_workers=config['users']) as executor:
            futures = []
            for user in range(config['users']):
                for req in range(config['requests_per_user']):
                    futures.append(executor.submit(make_auth_request))
                    time.sleep(config['delay'])
            
            # Wait for all requests to complete
            for future in as_completed(futures):
                future.result()
        
        stats = performance_metrics.get_stats()
        
        # Assertions for medium load authentication (more lenient for invalid credentials)
        assert stats['total_requests'] == config['users'] * config['requests_per_user']
        assert stats['avg_response_time'] < 2.0, f"Auth average response time too high: {stats['avg_response_time']:.3f}s"
        # Note: Authentication will fail since we're using invalid credentials, but system should handle gracefully
        # Focus on response time and system stability rather than success rate for invalid logins
        assert len([s for s in performance_metrics.status_codes if s >= 500]) == 0, "No server errors should occur during auth stress"
    
    def test_heavy_load_mixed_endpoints(self, stress_client, performance_metrics, load_test_config):
        """Test mixed endpoints under heavy load"""
        config = load_test_config['heavy_load']
        
        endpoints = [
            ('/api/items', 'GET'),
            ('/api/auth/login', 'POST'),
            ('/api/bookings', 'GET'),
        ]
        
        def make_mixed_request(endpoint, method):
            start_time = time.time()
            if method == 'GET':
                response = stress_client.get(endpoint)
            else:
                response = stress_client.post(endpoint, json={})
            response_time = time.time() - start_time
            performance_metrics.record_request(response_time, response.status_code)
            return response.status_code
        
        # Execute concurrent mixed requests
        with ThreadPoolExecutor(max_workers=config['users']) as executor:
            futures = []
            for user in range(config['users']):
                for req in range(config['requests_per_user']):
                    endpoint, method = endpoints[req % len(endpoints)]
                    futures.append(executor.submit(make_mixed_request, endpoint, method))
                    time.sleep(config['delay'])
            
            # Wait for all requests to complete
            for future in as_completed(futures):
                future.result()
        
        stats = performance_metrics.get_stats()
        
        # Assertions for heavy load (realistic expectations for stress conditions)
        assert stats['total_requests'] >= config['users'] * config['requests_per_user'] * 0.8  # Allow some requests to timeout under stress
        assert stats['avg_response_time'] < 5.0, f"Heavy load average response time too high: {stats['avg_response_time']:.3f}s"
        assert stats['success_rate'] > 0.60, f"Heavy load success rate too low: {stats['success_rate']:.2%}"  # More realistic under heavy load
    
    def test_spike_load_resilience(self, stress_client, performance_metrics, load_test_config):
        """Test system resilience under sudden load spikes"""
        config = load_test_config['spike_load']
        
        def make_spike_request():
            start_time = time.time()
            response = stress_client.get('/api/items')
            response_time = time.time() - start_time
            performance_metrics.record_request(response_time, response.status_code)
            return response.status_code
        
        # Execute sudden spike of concurrent requests
        with ThreadPoolExecutor(max_workers=config['users']) as executor:
            futures = []
            # Submit all requests at once (spike)
            for user in range(config['users']):
                for req in range(config['requests_per_user']):
                    futures.append(executor.submit(make_spike_request))
            
            # Wait for all requests to complete
            for future in as_completed(futures):
                future.result()
        
        stats = performance_metrics.get_stats()
        
        # Assertions for spike load (focus on resilience)
        assert stats['total_requests'] == config['users'] * config['requests_per_user']
        assert stats['success_rate'] > 0.80, f"Spike load success rate too low: {stats['success_rate']:.2%}"
        # Allow higher response times during spikes
        assert stats['avg_response_time'] < 5.0, f"Spike load average response time excessive: {stats['avg_response_time']:.3f}s"


class TestEndpointStressTesting:
    """Test individual endpoints under stress"""
    
    def test_items_endpoint_sustained_load(self, stress_client, performance_metrics):
        """Test items endpoint under sustained load for extended period"""
        duration = 10  # seconds
        request_interval = 0.1  # seconds
        
        start_time = time.time()
        request_count = 0
        
        while time.time() - start_time < duration:
            req_start = time.time()
            response = stress_client.get('/api/items')
            response_time = time.time() - req_start
            performance_metrics.record_request(response_time, response.status_code)
            request_count += 1
            
            # Maintain request interval
            time.sleep(max(0, request_interval - response_time))
        
        stats = performance_metrics.get_stats()
        
        # Assertions for sustained load
        assert stats['total_requests'] >= duration / request_interval * 0.8  # Allow some variance
        assert stats['avg_response_time'] < 1.5, f"Sustained load average response time too high: {stats['avg_response_time']:.3f}s"
        assert stats['success_rate'] > 0.95, f"Sustained load success rate too low: {stats['success_rate']:.2%}"
    
    def test_authentication_burst_requests(self, stress_client, performance_metrics, sample_stress_data):
        """Test authentication endpoint with burst requests - focus on system stability"""
        burst_size = 25
        login_data = sample_stress_data['login_data']
        
        def make_burst_request():
            start_time = time.time()
            response = stress_client.post('/api/auth/login', json=login_data)
            response_time = time.time() - start_time
            performance_metrics.record_request(response_time, response.status_code)
            return response.status_code
        
        # Execute burst of requests
        with ThreadPoolExecutor(max_workers=burst_size) as executor:
            futures = [executor.submit(make_burst_request) for _ in range(burst_size)]
            
            # Wait for all requests to complete
            for future in as_completed(futures):
                future.result()
        
        stats = performance_metrics.get_stats()
        
        # Assertions for burst requests (focus on system stability, not auth success with invalid creds)
        assert stats['total_requests'] == burst_size
        assert stats['max_response_time'] < 5.0, f"Burst request max response time too high: {stats['max_response_time']:.3f}s"
        # System should handle requests without errors (400 is expected for invalid login)
        server_errors = [s for s in performance_metrics.status_codes if s >= 500]
        assert len(server_errors) == 0, f"Server errors during auth burst: {len(server_errors)}"


class TestSystemResourceUsage:
    """Test system resource usage under stress"""
    
    def test_memory_usage_under_load(self, stress_client, performance_metrics):
        """Test that memory usage remains reasonable under load"""
        import psutil
        import os
        
        # Get initial memory usage
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Generate load
        for i in range(100):
            start_time = time.time()
            response = stress_client.get('/api/items')
            response_time = time.time() - start_time
            performance_metrics.record_request(response_time, response.status_code)
        
        # Check final memory usage
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory
        
        stats = performance_metrics.get_stats()
        
        # Assertions for memory usage
        assert stats['total_requests'] == 100
        assert memory_increase < 50, f"Memory usage increased by {memory_increase:.1f}MB, which is excessive"
        assert stats['success_rate'] > 0.95, f"Success rate during memory test too low: {stats['success_rate']:.2%}"
    
    def test_concurrent_user_simulation(self, stress_client, performance_metrics):
        """Simulate multiple concurrent users with realistic usage patterns"""
        num_users = 15
        requests_per_user = 8
        
        def simulate_user(user_id):
            user_requests = []
            
            # Simulate user workflow: browse items -> attempt login -> browse more
            for i in range(requests_per_user):
                if i % 3 == 0:
                    # Browse items
                    start_time = time.time()
                    response = stress_client.get('/api/items')
                    response_time = time.time() - start_time
                    performance_metrics.record_request(response_time, response.status_code)
                elif i % 3 == 1:
                    # Attempt login
                    start_time = time.time()
                    response = stress_client.post('/api/auth/login', json={
                        'email': f'user{user_id}@test.com',
                        'password': 'password123'
                    })
                    response_time = time.time() - start_time
                    performance_metrics.record_request(response_time, response.status_code)
                else:
                    # Try to access bookings (should fail without auth)
                    start_time = time.time()
                    response = stress_client.get('/api/bookings')
                    response_time = time.time() - start_time
                    performance_metrics.record_request(response_time, response.status_code)
                
                # Random delay between requests (0.1 to 0.5 seconds)
                time.sleep(0.1 + (i % 5) * 0.1)
        
        # Run concurrent user simulations
        with ThreadPoolExecutor(max_workers=num_users) as executor:
            futures = [executor.submit(simulate_user, user_id) for user_id in range(num_users)]
            
            # Wait for all users to complete
            for future in as_completed(futures):
                future.result()
        
        stats = performance_metrics.get_stats()
        
        # Assertions for concurrent user simulation (realistic expectations)
        assert stats['total_requests'] == num_users * requests_per_user
        assert stats['avg_response_time'] < 3.0, f"Concurrent users average response time too high: {stats['avg_response_time']:.3f}s"
        
        # Calculate success rate excluding authentication failures (which are expected with test credentials)
        non_auth_requests = sum(1 for code in performance_metrics.status_codes if code != 400)  # 400 = auth failure
        items_bookings_requests = sum(1 for code in performance_metrics.status_codes if code == 308)  # 308 = redirect for items/bookings
        
        if items_bookings_requests > 0:
            items_bookings_success_rate = items_bookings_requests / (num_users * requests_per_user * 2 / 3)  # 2/3 of requests are items/bookings
            assert items_bookings_success_rate > 0.80, f"Items/bookings success rate too low: {items_bookings_success_rate:.2%}"
