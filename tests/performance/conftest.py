"""
Performance testing configuration and fixtures
"""
import pytest
import time
import threading
import concurrent.futures
from contextlib import contextmanager
import psutil
import json
import statistics
from datetime import datetime
# Import from the main conftest - we want to reuse the same app setup
from tests.conftest import app


@pytest.fixture(scope='session')
def performance_client():
    """Performance testing client using the same app as integration tests"""
    # Import here to avoid circular imports
    from main import create_app
    
    app = create_app()
    app.config['TESTING'] = True
    app.config['JWT_SECRET_KEY'] = 'test_jwt_secret_for_performance'
    
    with app.test_client() as client:
        with app.app_context():
            yield client


@pytest.fixture
def concurrent_clients(request):
    """Create multiple concurrent test clients"""
    from main import create_app
    
    num_clients = getattr(request, 'param', 5)
    clients = []
    
    app = create_app()
    app.config['TESTING'] = True
    app.config['JWT_SECRET_KEY'] = 'test_jwt_secret_for_performance'
    
    for _ in range(num_clients):
        client = app.test_client()
        clients.append(client)
    
    return clients


@contextmanager
def performance_monitor():
    """Context manager to monitor performance metrics"""
    start_time = time.time()
    start_memory = psutil.Process().memory_info().rss / 1024 / 1024  # MB
    start_cpu = psutil.Process().cpu_percent()
    
    yield
    
    end_time = time.time()
    end_memory = psutil.Process().memory_info().rss / 1024 / 1024  # MB
    end_cpu = psutil.Process().cpu_percent()
    
    duration = end_time - start_time
    memory_diff = end_memory - start_memory
    cpu_usage = end_cpu
    
    print(f"\n--- Performance Metrics ---")
    print(f"Duration: {duration:.3f} seconds")
    print(f"Memory usage: {end_memory:.2f} MB (Δ {memory_diff:+.2f} MB)")
    print(f"CPU usage: {cpu_usage:.1f}%")


class PerformanceTest:
    """Base class for performance tests"""
    
    def __init__(self):
        self.results = []
        self.start_time = None
        self.end_time = None
    
    def start_timer(self):
        """Start performance timing"""
        self.start_time = time.time()
    
    def end_timer(self):
        """End performance timing and record result"""
        self.end_time = time.time()
        duration = self.end_time - self.start_time
        self.results.append(duration)
        return duration
    
    def get_statistics(self):
        """Get performance statistics"""
        if not self.results:
            return {}
        
        return {
            'count': len(self.results),
            'min': min(self.results),
            'max': max(self.results),
            'mean': statistics.mean(self.results),
            'median': statistics.median(self.results),
            'std_dev': statistics.stdev(self.results) if len(self.results) > 1 else 0
        }
    
    def assert_performance(self, max_duration=None, max_mean=None):
        """Assert performance requirements"""
        stats = self.get_statistics()
        
        if max_duration and stats.get('max', 0) > max_duration:
            pytest.fail(f"Maximum duration {stats['max']:.3f}s exceeds limit {max_duration}s")
        
        if max_mean and stats.get('mean', 0) > max_mean:
            pytest.fail(f"Mean duration {stats['mean']:.3f}s exceeds limit {max_mean}s")


@pytest.fixture
def performance_test():
    """Performance test helper fixture"""
    return PerformanceTest()


def concurrent_request_executor(clients, endpoint, method='GET', data=None, iterations=10):
    """Execute concurrent requests across multiple clients"""
    results = []
    
    def make_request(client_index):
        # Create a fresh client for each thread to avoid context issues
        from main import create_app
        app = create_app()
        app.config['TESTING'] = True
        app.config['JWT_SECRET_KEY'] = 'test_jwt_secret_for_performance'
        
        response_times = []
        with app.test_client() as client:
            for _ in range(iterations):
                start = time.time()
                
                try:
                    if method == 'GET':
                        response = client.get(endpoint)
                    elif method == 'POST':
                        response = client.post(endpoint, 
                                             data=json.dumps(data) if data else None,
                                             content_type='application/json')
                    elif method == 'PUT':
                        response = client.put(endpoint,
                                            data=json.dumps(data) if data else None,
                                            content_type='application/json')
                    elif method == 'DELETE':
                        response = client.delete(endpoint)
                    
                    end = time.time()
                    response_times.append({
                        'duration': end - start,
                        'status_code': response.status_code,
                        'timestamp': datetime.now().isoformat()
                    })
                except Exception as e:
                    end = time.time()
                    response_times.append({
                        'duration': end - start,
                        'status_code': 500,
                        'timestamp': datetime.now().isoformat(),
                        'error': str(e)
                    })
        
        return response_times
    
    # Execute requests concurrently
    with concurrent.futures.ThreadPoolExecutor(max_workers=len(clients)) as executor:
        futures = [executor.submit(make_request, i) for i in range(len(clients))]
        
        for future in concurrent.futures.as_completed(futures):
            try:
                results.extend(future.result())
            except Exception as e:
                # Handle executor exceptions gracefully
                results.append({
                    'duration': 0,
                    'status_code': 500,
                    'timestamp': datetime.now().isoformat(),
                    'error': str(e)
                })
    
    return results


@pytest.fixture
def load_test_executor():
    """Load testing executor fixture"""
    return concurrent_request_executor


class DatabasePerformanceMonitor:
    """Monitor database performance during tests"""
    
    def __init__(self):
        self.query_times = []
        self.connection_times = []
    
    @contextmanager
    def monitor_query(self, operation_name):
        """Monitor database query performance"""
        start = time.time()
        try:
            yield
        finally:
            duration = time.time() - start
            self.query_times.append({
                'operation': operation_name,
                'duration': duration,
                'timestamp': datetime.now().isoformat()
            })
    
    def get_query_statistics(self):
        """Get database query statistics"""
        if not self.query_times:
            return {}
        
        durations = [q['duration'] for q in self.query_times]
        return {
            'total_queries': len(durations),
            'min_duration': min(durations),
            'max_duration': max(durations),
            'avg_duration': statistics.mean(durations),
            'total_time': sum(durations)
        }


@pytest.fixture
def db_performance_monitor():
    """Database performance monitor fixture"""
    return DatabasePerformanceMonitor()
