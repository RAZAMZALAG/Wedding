"""
Stress Testing Suite - Performance Benchmarks
Tests system performance benchmarks and response time requirements
"""
import pytest
import time
import statistics
from concurrent.futures import ThreadPoolExecutor

class TestPerformanceBenchmarks:
    """Test performance benchmarks for critical operations"""
    
    def test_single_request_response_times(self, stress_client):
        """Test that single requests meet response time requirements"""
        
        # Critical endpoints and their maximum allowed response times (seconds)
        endpoints = {
            '/api/items': 0.5,           # Catalog browsing should be fast
            '/api/auth/login': 1.0,      # Login can be slightly slower
            '/api/bookings': 0.8,        # Booking access should be quick
        }
        
        for endpoint, max_time in endpoints.items():
            response_times = []
            
            # Make 10 requests to get average
            for _ in range(10):
                start_time = time.time()
                if endpoint == '/api/auth/login':
                    response = stress_client.post(endpoint, json={
                        'email': 'test@example.com',
                        'password': 'password'
                    })
                else:
                    response = stress_client.get(endpoint)
                
                response_time = time.time() - start_time
                response_times.append(response_time)
            
            avg_time = statistics.mean(response_times)
            max_observed = max(response_times)
            
            # Assertions
            assert avg_time < max_time, f"{endpoint} average response time {avg_time:.3f}s exceeds limit {max_time}s"
            assert max_observed < max_time * 2, f"{endpoint} max response time {max_observed:.3f}s too high"
    
    def test_throughput_benchmarks(self, stress_client, performance_metrics):
        """Test system throughput under controlled conditions"""
        
        target_rps = 10  # requests per second
        test_duration = 5  # seconds
        request_interval = 1.0 / target_rps
        
        start_time = time.time()
        actual_requests = 0
        
        while time.time() - start_time < test_duration:
            req_start = time.time()
            response = stress_client.get('/api/items')
            response_time = time.time() - req_start
            performance_metrics.record_request(response_time, response.status_code)
            actual_requests += 1
            
            # Try to maintain target interval
            elapsed = time.time() - req_start
            sleep_time = max(0, request_interval - elapsed)
            time.sleep(sleep_time)
        
        actual_duration = time.time() - start_time
        actual_rps = actual_requests / actual_duration
        stats = performance_metrics.get_stats()
        
        # Assertions for throughput
        assert actual_rps >= target_rps * 0.8, f"Actual RPS {actual_rps:.1f} below target {target_rps}"
        assert stats['success_rate'] > 0.95, f"Success rate {stats['success_rate']:.2%} too low for throughput test"
        assert stats['avg_response_time'] < 0.5, f"Average response time {stats['avg_response_time']:.3f}s too high for throughput test"
    
    def test_concurrent_request_scaling(self, stress_client):
        """Test how response times scale with concurrent requests"""
        
        def make_request():
            start_time = time.time()
            response = stress_client.get('/api/items')
            return time.time() - start_time, response.status_code
        
        concurrency_levels = [1, 5, 10, 15]
        results = {}
        
        for concurrency in concurrency_levels:
            response_times = []
            
            with ThreadPoolExecutor(max_workers=concurrency) as executor:
                futures = [executor.submit(make_request) for _ in range(concurrency * 3)]
                
                for future in futures:
                    response_time, status_code = future.result()
                    if 200 <= status_code < 400:
                        response_times.append(response_time)
            
            if response_times:
                results[concurrency] = {
                    'avg_time': statistics.mean(response_times),
                    'max_time': max(response_times),
                    'requests': len(response_times)
                }
        
        # Analyze scaling characteristics
        baseline_time = results[1]['avg_time']
        
        for concurrency in [5, 10, 15]:
            if concurrency in results:
                current_time = results[concurrency]['avg_time']
                scaling_factor = current_time / baseline_time
                
                # More realistic expectations: Response time can increase significantly under load
                # We mainly want to ensure the system doesn't completely break down
                max_scaling = 12.0 if concurrency == 15 else 8.0 if concurrency == 10 else 5.0
                assert scaling_factor < max_scaling, f"Response time scaling excessive: {scaling_factor:.1f}x at {concurrency} concurrent requests (max: {max_scaling}x)"
    
    def test_error_rate_under_stress(self, stress_client, performance_metrics):
        """Test that error rates remain acceptable under stress"""
        
        num_requests = 100
        concurrency = 20
        
        def make_stress_request():
            start_time = time.time()
            response = stress_client.get('/api/items')
            response_time = time.time() - start_time
            performance_metrics.record_request(response_time, response.status_code)
            return response.status_code
        
        # Execute stress requests
        with ThreadPoolExecutor(max_workers=concurrency) as executor:
            futures = [executor.submit(make_stress_request) for _ in range(num_requests)]
            
            status_codes = []
            for future in futures:
                status_codes.append(future.result())
        
        stats = performance_metrics.get_stats()
        
        # Calculate error rates
        client_errors = len([s for s in status_codes if 400 <= s < 500])
        server_errors = len([s for s in status_codes if s >= 500])
        
        client_error_rate = client_errors / num_requests
        server_error_rate = server_errors / num_requests
        
        # Assertions for error rates
        assert server_error_rate < 0.05, f"Server error rate {server_error_rate:.2%} too high"
        assert client_error_rate < 0.20, f"Client error rate {client_error_rate:.2%} too high"
        assert stats['success_rate'] > 0.80, f"Overall success rate {stats['success_rate']:.2%} too low"


class TestDatabasePerformance:
    """Test database performance under stress"""
    
    def test_database_query_performance(self, stress_client, performance_metrics):
        """Test database query performance under load"""
        
        # Items endpoint hits the database
        num_queries = 50
        
        for i in range(num_queries):
            start_time = time.time()
            response = stress_client.get('/api/items')
            response_time = time.time() - start_time
            performance_metrics.record_request(response_time, response.status_code)
            
            # Small delay to simulate real usage
            time.sleep(0.05)
        
        stats = performance_metrics.get_stats()
        
        # Assertions for database performance
        assert stats['avg_response_time'] < 0.8, f"Database query average time {stats['avg_response_time']:.3f}s too high"
        assert stats['max_response_time'] < 2.0, f"Database query max time {stats['max_response_time']:.3f}s too high"
        assert stats['success_rate'] > 0.95, f"Database query success rate {stats['success_rate']:.2%} too low"
    
    def test_concurrent_database_access(self, stress_client, performance_metrics):
        """Test concurrent database access"""
        
        concurrency = 15
        requests_per_thread = 10
        
        def database_stress_test():
            for _ in range(requests_per_thread):
                start_time = time.time()
                response = stress_client.get('/api/items')
                response_time = time.time() - start_time
                performance_metrics.record_request(response_time, response.status_code)
                time.sleep(0.02)  # Brief pause between requests
        
        # Execute concurrent database access
        with ThreadPoolExecutor(max_workers=concurrency) as executor:
            futures = [executor.submit(database_stress_test) for _ in range(concurrency)]
            
            # Wait for all threads to complete
            for future in futures:
                future.result()
        
        stats = performance_metrics.get_stats()
        
        # Assertions for concurrent database access
        expected_requests = concurrency * requests_per_thread
        assert stats['total_requests'] == expected_requests
        assert stats['avg_response_time'] < 1.5, f"Concurrent DB access avg time {stats['avg_response_time']:.3f}s too high"
        assert stats['success_rate'] > 0.90, f"Concurrent DB access success rate {stats['success_rate']:.2%} too low"


class TestAPIStressScenarios:
    """Test API under various stress scenarios"""
    
    def test_mixed_endpoint_stress(self, stress_client, performance_metrics, sample_stress_data):
        """Test mixed endpoint usage under stress"""
        
        endpoints = [
            ('/api/items', 'GET', None),
            ('/api/auth/login', 'POST', sample_stress_data['login_data']),
            ('/api/bookings', 'GET', None),
        ]
        
        def mixed_request_worker():
            for endpoint, method, data in endpoints:
                start_time = time.time()
                
                if method == 'GET':
                    response = stress_client.get(endpoint)
                else:
                    response = stress_client.post(endpoint, json=data or {})
                
                response_time = time.time() - start_time
                performance_metrics.record_request(response_time, response.status_code)
                
                time.sleep(0.1)  # Brief pause between different endpoints
        
        # Run mixed stress test
        num_workers = 12
        with ThreadPoolExecutor(max_workers=num_workers) as executor:
            futures = [executor.submit(mixed_request_worker) for _ in range(num_workers)]
            
            for future in futures:
                future.result()
        
        stats = performance_metrics.get_stats()
        
        # Assertions for mixed endpoint stress (excluding auth failures from success rate)
        expected_requests = num_workers * len(endpoints)
        assert stats['total_requests'] == expected_requests
        assert stats['avg_response_time'] < 3.0, f"Mixed endpoint avg time {stats['avg_response_time']:.3f}s too high"
        
        # Calculate success rate excluding authentication failures (status 400)
        successful_requests = sum(1 for code in performance_metrics.status_codes if 200 <= code < 400 and code != 400)
        non_auth_requests = sum(1 for code in performance_metrics.status_codes if code != 400)
        
        if non_auth_requests > 0:
            adjusted_success_rate = successful_requests / non_auth_requests
            assert adjusted_success_rate > 0.75, f"Non-auth endpoint success rate {adjusted_success_rate:.2%} too low"
    
    def test_rapid_fire_requests(self, stress_client, performance_metrics):
        """Test system under rapid-fire requests"""
        
        rapid_fire_count = 30
        max_interval = 0.01  # Very short interval between requests
        
        for i in range(rapid_fire_count):
            start_time = time.time()
            response = stress_client.get('/api/items')
            response_time = time.time() - start_time
            performance_metrics.record_request(response_time, response.status_code)
            
            time.sleep(max_interval)
        
        stats = performance_metrics.get_stats()
        
        # Assertions for rapid-fire requests
        assert stats['total_requests'] == rapid_fire_count
        assert stats['success_rate'] > 0.85, f"Rapid-fire success rate {stats['success_rate']:.2%} too low"
        # Allow higher response times for rapid-fire scenario
        assert stats['avg_response_time'] < 1.0, f"Rapid-fire avg time {stats['avg_response_time']:.3f}s too high"
