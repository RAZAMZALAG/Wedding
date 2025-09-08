"""
Stress Testing Suite - System Resilience
Tests system resilience, recovery, and stability under extreme conditions
"""
import pytest
import time
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
import random

class TestSystemResilience:
    """Test system resilience under extreme stress conditions"""
    
    def test_extreme_concurrent_load(self, stress_client, performance_metrics):
        """Test system behavior under extreme concurrent load"""
        
        extreme_concurrency = 50
        requests_per_thread = 5
        
        def extreme_load_worker():
            for _ in range(requests_per_thread):
                start_time = time.time()
                response = stress_client.get('/api/items')
                response_time = time.time() - start_time
                performance_metrics.record_request(response_time, response.status_code)
                # No delay - maximum stress
        
        # Execute extreme load
        with ThreadPoolExecutor(max_workers=extreme_concurrency) as executor:
            futures = [executor.submit(extreme_load_worker) for _ in range(extreme_concurrency)]
            
            completed = 0
            for future in as_completed(futures):
                future.result()
                completed += 1
        
        stats = performance_metrics.get_stats()
        
        # Assertions for extreme load (focus on not crashing)
        expected_requests = extreme_concurrency * requests_per_thread
        assert stats['total_requests'] == expected_requests
        # Allow degraded performance but system should not crash
        assert stats['success_rate'] > 0.60, f"Extreme load success rate {stats['success_rate']:.2%} - system may be overloaded"
        # Allow high response times under extreme stress
        assert stats['avg_response_time'] < 10.0, f"Extreme load avg time {stats['avg_response_time']:.3f}s - system unresponsive"
    
    def test_sustained_stress_endurance(self, stress_client, performance_metrics):
        """Test system endurance under sustained stress"""
        
        duration = 30  # seconds
        request_rate = 5  # requests per second
        request_interval = 1.0 / request_rate
        
        start_time = time.time()
        requests_made = 0
        
        while time.time() - start_time < duration:
            req_start = time.time()
            response = stress_client.get('/api/items')
            response_time = time.time() - req_start
            performance_metrics.record_request(response_time, response.status_code)
            requests_made += 1
            
            # Maintain request rate
            elapsed = time.time() - req_start
            sleep_time = max(0, request_interval - elapsed)
            time.sleep(sleep_time)
        
        stats = performance_metrics.get_stats()
        
        # Assertions for endurance test
        expected_min_requests = duration * request_rate * 0.8  # Allow 20% variance
        assert stats['total_requests'] >= expected_min_requests, f"Made {stats['total_requests']} requests, expected at least {expected_min_requests}"
        assert stats['success_rate'] > 0.85, f"Endurance success rate {stats['success_rate']:.2%} too low"
        assert stats['avg_response_time'] < 2.0, f"Endurance avg time {stats['avg_response_time']:.3f}s degraded over time"
    
    def test_memory_leak_detection(self, stress_client, performance_metrics):
        """Test for memory leaks under sustained load"""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        
        # Baseline memory measurement
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Generate sustained load
        num_requests = 200
        for i in range(num_requests):
            start_time = time.time()
            response = stress_client.get('/api/items')
            response_time = time.time() - start_time
            performance_metrics.record_request(response_time, response.status_code)
            
            # Measure memory every 50 requests
            if i % 50 == 0:
                current_memory = process.memory_info().rss / 1024 / 1024
                memory_growth = current_memory - initial_memory
                # Alert if memory grows more than 100MB during test
                assert memory_growth < 100, f"Potential memory leak: {memory_growth:.1f}MB growth after {i} requests"
        
        # Final memory check
        final_memory = process.memory_info().rss / 1024 / 1024
        total_growth = final_memory - initial_memory
        
        stats = performance_metrics.get_stats()
        
        # Assertions for memory leak detection
        assert stats['total_requests'] == num_requests
        assert total_growth < 50, f"Memory grew {total_growth:.1f}MB during test - possible leak"
        assert stats['success_rate'] > 0.90, f"Memory test success rate {stats['success_rate']:.2%} too low"
    
    def test_random_load_patterns(self, stress_client, performance_metrics):
        """Test system with random, unpredictable load patterns"""
        
        duration = 20  # seconds
        start_time = time.time()
        
        def random_burst_worker():
            while time.time() - start_time < duration:
                # Random burst size (1-10 requests)
                burst_size = random.randint(1, 10)
                
                for _ in range(burst_size):
                    req_start = time.time()
                    response = stress_client.get('/api/items')
                    response_time = time.time() - req_start
                    performance_metrics.record_request(response_time, response.status_code)
                
                # Random pause between bursts (0.1-2.0 seconds)
                pause = random.uniform(0.1, 2.0)
                time.sleep(pause)
        
        # Run multiple random workers
        num_workers = 8
        with ThreadPoolExecutor(max_workers=num_workers) as executor:
            futures = [executor.submit(random_burst_worker) for _ in range(num_workers)]
            
            for future in as_completed(futures):
                future.result()
        
        stats = performance_metrics.get_stats()
        
        # Assertions for random load patterns
        assert stats['total_requests'] > 50, f"Random load generated only {stats['total_requests']} requests"
        assert stats['success_rate'] > 0.80, f"Random load success rate {stats['success_rate']:.2%} too low"
        assert stats['avg_response_time'] < 3.0, f"Random load avg time {stats['avg_response_time']:.3f}s too high"


class TestFailureRecovery:
    """Test system recovery from various failure scenarios"""
    
    def test_rapid_authentication_attempts(self, stress_client, performance_metrics, sample_stress_data):
        """Test system handling rapid authentication attempts"""
        
        login_data = sample_stress_data['login_data']
        rapid_attempts = 30
        
        def rapid_auth_attempt():
            start_time = time.time()
            response = stress_client.post('/api/auth/login', json=login_data)
            response_time = time.time() - start_time
            performance_metrics.record_request(response_time, response.status_code)
            return response.status_code
        
        # Execute rapid authentication attempts
        with ThreadPoolExecutor(max_workers=15) as executor:
            futures = [executor.submit(rapid_auth_attempt) for _ in range(rapid_attempts)]
            
            status_codes = []
            for future in as_completed(futures):
                status_codes.append(future.result())
        
        stats = performance_metrics.get_stats()
        
        # Assertions for rapid auth attempts
        assert stats['total_requests'] == rapid_attempts
        # System should handle auth attempts gracefully (even if they fail)
        assert stats['avg_response_time'] < 3.0, f"Rapid auth avg time {stats['avg_response_time']:.3f}s too high"
        # Should not crash the system
        server_errors = len([s for s in status_codes if s >= 500])
        assert server_errors / rapid_attempts < 0.1, f"Too many server errors: {server_errors}/{rapid_attempts}"
    
    def test_malformed_request_handling(self, stress_client, performance_metrics):
        """Test system handling of malformed requests under stress"""
        
        malformed_requests = [
            ('/api/items', 'POST', {'invalid': 'data'}),
            ('/api/auth/login', 'POST', {'malformed': True}),
            ('/api/bookings', 'POST', 'not_json'),
            ('/api/nonexistent', 'GET', None),
        ]
        
        def malformed_request_worker():
            for endpoint, method, data in malformed_requests:
                start_time = time.time()
                
                try:
                    if method == 'GET':
                        response = stress_client.get(endpoint)
                    else:
                        if isinstance(data, str):
                            response = stress_client.post(endpoint, data=data)
                        else:
                            response = stress_client.post(endpoint, json=data)
                    
                    response_time = time.time() - start_time
                    performance_metrics.record_request(response_time, response.status_code)
                except Exception as e:
                    response_time = time.time() - start_time
                    performance_metrics.record_request(response_time, 500, str(e))
        
        # Run malformed request tests
        num_workers = 10
        with ThreadPoolExecutor(max_workers=num_workers) as executor:
            futures = [executor.submit(malformed_request_worker) for _ in range(num_workers)]
            
            for future in as_completed(futures):
                future.result()
        
        stats = performance_metrics.get_stats()
        
        # Assertions for malformed request handling
        expected_requests = num_workers * len(malformed_requests)
        assert stats['total_requests'] == expected_requests
        assert stats['avg_response_time'] < 1.0, f"Malformed request handling avg time {stats['avg_response_time']:.3f}s too high"
        # Should gracefully handle malformed requests, not crash
        assert len(stats.get('errors', [])) / expected_requests < 0.2, "Too many errors processing malformed requests"
    
    def test_connection_stress_recovery(self, stress_client, performance_metrics):
        """Test system recovery after connection stress"""
        
        # Phase 1: Generate high connection stress
        stress_phase_duration = 10  # seconds
        stress_start = time.time()
        
        def connection_stress_worker():
            while time.time() - stress_start < stress_phase_duration:
                req_start = time.time()
                response = stress_client.get('/api/items')
                response_time = time.time() - req_start
                performance_metrics.record_request(response_time, response.status_code)
                # Minimal delay for maximum stress
                time.sleep(0.01)
        
        # Create stress with many workers
        stress_workers = 25
        with ThreadPoolExecutor(max_workers=stress_workers) as executor:
            stress_futures = [executor.submit(connection_stress_worker) for _ in range(stress_workers)]
            
            for future in as_completed(stress_futures):
                future.result()
        
        # Phase 2: Test recovery with normal load
        time.sleep(2)  # Brief recovery period
        
        recovery_requests = 20
        for _ in range(recovery_requests):
            start_time = time.time()
            response = stress_client.get('/api/items')
            response_time = time.time() - start_time
            performance_metrics.record_request(response_time, response.status_code)
            time.sleep(0.1)  # Normal request interval
        
        stats = performance_metrics.get_stats()
        
        # Assertions for stress recovery
        total_expected = recovery_requests + (stress_workers * stress_phase_duration * 10)  # Rough estimate
        assert stats['total_requests'] >= recovery_requests, f"Recovery phase generated {stats['total_requests']} requests"
        assert stats['success_rate'] > 0.70, f"Overall success rate {stats['success_rate']:.2%} too low during stress/recovery"


class TestScalabilityLimits:
    """Test system behavior at scalability limits"""
    
    def test_maximum_concurrent_connections(self, stress_client, performance_metrics):
        """Test maximum concurrent connections the system can handle"""
        
        max_connections = 100  # Test up to 100 concurrent connections
        connection_duration = 5  # seconds each connection stays active
        
        def sustained_connection_worker():
            requests_per_connection = connection_duration * 2  # 2 requests per second
            
            for _ in range(requests_per_connection):
                start_time = time.time()
                response = stress_client.get('/api/items')
                response_time = time.time() - start_time
                performance_metrics.record_request(response_time, response.status_code)
                time.sleep(0.5)  # 2 requests per second
        
        # Test with maximum connections
        with ThreadPoolExecutor(max_workers=max_connections) as executor:
            futures = [executor.submit(sustained_connection_worker) for _ in range(max_connections)]
            
            completed_connections = 0
            for future in as_completed(futures):
                future.result()
                completed_connections += 1
        
        stats = performance_metrics.get_stats()
        
        # Assertions for maximum connections
        assert completed_connections == max_connections, f"Only {completed_connections}/{max_connections} connections completed"
        assert stats['success_rate'] > 0.50, f"Max connection success rate {stats['success_rate']:.2%} - system overloaded"
        # Allow high response times at maximum capacity
        assert stats['avg_response_time'] < 15.0, f"Max connection avg time {stats['avg_response_time']:.3f}s - system unresponsive"
    
    def test_request_queue_limits(self, stress_client, performance_metrics):
        """Test system behavior when request queues are full"""
        
        queue_overflow_requests = 200
        burst_concurrency = 100
        
        def queue_overflow_worker():
            start_time = time.time()
            response = stress_client.get('/api/items')
            response_time = time.time() - start_time
            performance_metrics.record_request(response_time, response.status_code)
            return response.status_code
        
        # Create request queue overflow
        with ThreadPoolExecutor(max_workers=burst_concurrency) as executor:
            futures = [executor.submit(queue_overflow_worker) for _ in range(queue_overflow_requests)]
            
            completed_requests = 0
            for future in as_completed(futures):
                future.result()
                completed_requests += 1
        
        stats = performance_metrics.get_stats()
        
        # Assertions for queue limits
        assert stats['total_requests'] == queue_overflow_requests
        assert completed_requests == queue_overflow_requests, f"Only {completed_requests}/{queue_overflow_requests} requests completed"
        # System should handle queue overflow gracefully
        assert stats['success_rate'] > 0.40, f"Queue overflow success rate {stats['success_rate']:.2%} - queue management failing"
