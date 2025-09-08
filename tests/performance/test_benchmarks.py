"""
Performance benchmarking for core system operations
Tests response times and throughput for critical functions
"""
import pytest
import time
import json
from datetime import datetime, timedelta
import statistics
from tests.performance.conftest import (
    performance_monitor, performance_test, performance_client
)


class TestPerformanceBenchmarks:
    """Performance benchmarks for core operations"""
    
    def test_catalog_loading_performance(self, performance_client, performance_test):
        """Benchmark catalog loading performance"""
        iterations = 20
        
        for i in range(iterations):
            performance_test.start_timer()
            response = performance_client.get('/api/items/')
            performance_test.end_timer()
            
            # Basic functionality check
            assert response.status_code in [200, 401]
        
        # Performance assertions
        stats = performance_test.get_statistics()
        performance_test.assert_performance(max_mean=1.0, max_duration=3.0)
        
        print(f"\n--- Catalog Loading Benchmark ---")
        print(f"Iterations: {stats['count']}")
        print(f"Mean response time: {stats['mean']:.3f}s")
        print(f"Median response time: {stats['median']:.3f}s")
        print(f"95th percentile: {sorted(performance_test.results)[int(len(performance_test.results) * 0.95)]:.3f}s")
    
    def test_authentication_performance(self, performance_client, performance_test):
        """Benchmark authentication performance"""
        login_data = {
            'email': 'admin@email.com',
            'password': 'admin123'
        }
        
        iterations = 15
        
        for i in range(iterations):
            performance_test.start_timer()
            response = performance_client.post('/api/auth/login',
                                             data=json.dumps(login_data),
                                             content_type='application/json')
            performance_test.end_timer()
            
            # Should handle auth requests
            assert response.status_code in [200, 400, 422]
        
        # Performance assertions - auth should be fast
        stats = performance_test.get_statistics()
        performance_test.assert_performance(max_mean=0.5, max_duration=2.0)
        
        print(f"\n--- Authentication Benchmark ---")
        print(f"Iterations: {stats['count']}")
        print(f"Mean response time: {stats['mean']:.3f}s")
        print(f"Max response time: {stats['max']:.3f}s")
    
    def test_ai_assistant_performance(self, performance_client, performance_test):
        """Benchmark AI assistant performance"""
        test_messages = [
            {'message': 'Help me plan my wedding', 'language': 'en'},
            {'message': 'What items do you recommend?', 'language': 'en'},
            {'message': 'שלום, אני צריכה עזרה עם התכנון', 'language': 'he'},
            {'message': 'Show me wedding tables', 'language': 'en'},
            {'message': 'Wedding planning assistance needed', 'language': 'en'}
        ]
        
        for message_data in test_messages[:3]:  # Limit to avoid excessive AI calls
            performance_test.start_timer()
            response = performance_client.post('/api/ai/chat',
                                             data=json.dumps(message_data),
                                             content_type='application/json')
            performance_test.end_timer()
            
            # AI endpoint should respond (may require auth/API key, or quota limits)
            assert response.status_code in [200, 400, 401, 422]
        
        stats = performance_test.get_statistics()
        
        if stats['count'] > 0:
            # AI responses can be slower but should be reasonable
            assert stats['mean'] < 15.0, f"AI responses too slow: {stats['mean']:.3f}s"
            assert stats['max'] < 30.0, f"AI max response time too high: {stats['max']:.3f}s"
            
            print(f"\n--- AI Assistant Benchmark ---")
            print(f"Iterations: {stats['count']}")
            print(f"Mean response time: {stats['mean']:.3f}s")
            print(f"Max response time: {stats['max']:.3f}s")
    
    def test_database_query_performance(self, performance_client, performance_test):
        """Benchmark database query performance"""
        endpoints_to_test = [
            '/api/items/',
            '/api/auth/verify',
            '/api/categories'
        ]
        
        for endpoint in endpoints_to_test:
            # Test each endpoint multiple times
            for i in range(5):
                performance_test.start_timer()
                response = performance_client.get(endpoint)
                performance_test.end_timer()
                
                # Should not crash
                assert response.status_code != 500
        
        stats = performance_test.get_statistics()
        
        # Database queries should be fast
        performance_test.assert_performance(max_mean=2.0, max_duration=5.0)
        
        print(f"\n--- Database Query Benchmark ---")
        print(f"Total queries: {stats['count']}")
        print(f"Mean query time: {stats['mean']:.3f}s")
        print(f"Slowest query: {stats['max']:.3f}s")
    
    def test_booking_operations_performance(self, performance_client, performance_test):
        """Benchmark booking-related operations"""
        booking_operations = [
            ('/api/bookings/', 'GET'),
            ('/api/bookings/lock-items', 'POST', {
                'start_date': '2025-12-01',
                'end_date': '2025-12-03'
            }),
            ('/api/bookings/release-locks', 'DELETE')
        ]
        
        for endpoint, method, *data in booking_operations:
            request_data = data[0] if data else None
            
            performance_test.start_timer()
            
            if method == 'GET':
                response = performance_client.get(endpoint)
            elif method == 'POST':
                response = performance_client.post(endpoint,
                                                 data=json.dumps(request_data) if request_data else None,
                                                 content_type='application/json')
            elif method == 'DELETE':
                response = performance_client.delete(endpoint)
            
            performance_test.end_timer()
            
            # Should handle booking operations
            assert response.status_code in [200, 400, 401, 404, 422]
        
        stats = performance_test.get_statistics()
        
        # Booking operations should be responsive
        performance_test.assert_performance(max_mean=3.0, max_duration=10.0)
        
        print(f"\n--- Booking Operations Benchmark ---")
        print(f"Operations tested: {stats['count']}")
        print(f"Mean operation time: {stats['mean']:.3f}s")
        print(f"Max operation time: {stats['max']:.3f}s")
    
    def test_json_processing_performance(self, performance_client, performance_test):
        """Benchmark JSON processing performance"""
        # Test with various payload sizes
        test_payloads = [
            {'message': 'small'},
            {'message': 'medium ' * 50},
            {'message': 'large ' * 200, 'data': list(range(100))},
            {
                'complex_data': {
                    'items': [{'id': i, 'name': f'item_{i}'} for i in range(50)],
                    'message': 'complex payload test'
                }
            }
        ]
        
        for payload in test_payloads:
            performance_test.start_timer()
            response = performance_client.post('/api/ai/chat',
                                             data=json.dumps(payload),
                                             content_type='application/json')
            performance_test.end_timer()
            
            # Should handle JSON processing
            assert response.status_code in [200, 400, 401, 422]
        
        stats = performance_test.get_statistics()
        
        # JSON processing should be fast
        performance_test.assert_performance(max_mean=5.0, max_duration=15.0)
        
        print(f"\n--- JSON Processing Benchmark ---")
        print(f"Payloads tested: {stats['count']}")
        print(f"Mean processing time: {stats['mean']:.3f}s")
    
    def test_error_handling_performance(self, performance_client, performance_test):
        """Benchmark error handling performance"""
        error_scenarios = [
            ('/api/nonexistent', 'GET'),
            ('/api/items/invalid_id', 'GET'),
            ('/api/auth/login', 'POST', {'invalid': 'data'}),
            ('/api/bookings/', 'POST', {'malformed': 'request'})
        ]
        
        for endpoint, method, *data in error_scenarios:
            request_data = data[0] if data else None
            
            performance_test.start_timer()
            
            if method == 'GET':
                response = performance_client.get(endpoint)
            elif method == 'POST':
                response = performance_client.post(endpoint,
                                                 data=json.dumps(request_data) if request_data else None,
                                                 content_type='application/json')
            
            performance_test.end_timer()
            
            # Should handle errors gracefully (may return 200 for some endpoints)
            assert response.status_code in [200, 400, 401, 404, 422, 500]
        
        stats = performance_test.get_statistics()
        
        # Error handling should be fast
        performance_test.assert_performance(max_mean=1.0, max_duration=3.0)
        
        print(f"\n--- Error Handling Benchmark ---")
        print(f"Error scenarios tested: {stats['count']}")
        print(f"Mean error handling time: {stats['mean']:.3f}s")


class TestThroughputBenchmarks:
    """Throughput benchmarks for system capacity"""
    
    def test_requests_per_second_catalog(self, performance_client):
        """Measure requests per second for catalog endpoint"""
        duration = 10  # seconds
        request_count = 0
        start_time = time.time()
        
        while time.time() - start_time < duration:
            response = performance_client.get('/api/items/')
            assert response.status_code in [200, 401]
            request_count += 1
        
        actual_duration = time.time() - start_time
        rps = request_count / actual_duration
        
        print(f"\n--- Catalog Throughput Test ---")
        print(f"Duration: {actual_duration:.1f}s")
        print(f"Total requests: {request_count}")
        print(f"Requests per second: {rps:.2f}")
        
        # Should handle at least 5 requests per second
        assert rps >= 5.0, f"Catalog throughput too low: {rps:.2f} RPS"
    
    def test_sustained_load_endurance(self, performance_client):
        """Test system behavior under sustained load"""
        duration = 30  # seconds
        request_times = []
        error_count = 0
        start_time = time.time()
        
        while time.time() - start_time < duration:
            request_start = time.time()
            response = performance_client.get('/api/items/')
            request_end = time.time()
            
            request_times.append(request_end - request_start)
            
            if response.status_code >= 500:
                error_count += 1
        
        # Analysis
        total_requests = len(request_times)
        mean_response_time = statistics.mean(request_times)
        error_rate = error_count / total_requests if total_requests > 0 else 0
        
        print(f"\n--- Sustained Load Endurance Test ---")
        print(f"Duration: {duration}s")
        print(f"Total requests: {total_requests}")
        print(f"Mean response time: {mean_response_time:.3f}s")
        print(f"Error rate: {error_rate:.2%}")
        
        # Performance should not degrade significantly
        assert mean_response_time < 3.0, f"Performance degraded under sustained load: {mean_response_time:.3f}s"
        assert error_rate < 0.1, f"Error rate too high under sustained load: {error_rate:.2%}"
