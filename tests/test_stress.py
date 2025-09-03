import os
import pytest
from client2 import Client
from test_client2_ForStudents import MockDBConnection

# Get the path to the current directory to ensure files are always found
current_dir = os.path.dirname(__file__)


# Stress Test 1
def test_stress_insert_many_users():
    """
    This stress test inserts a large number of users into the mocked DB
    to verify the Client can handle bulk inserts without errors or slowdown.
    """
    mock_db = MockDBConnection()
    client = Client(mock_db)

    for i in range(1000):  # simulate heavy load
        client.add_user(f"user{i}", i % 100)

    # Verify that the last user exists
    result = client.get_user("user999")
    assert result["age"] == 99


# Stress Test 2
def test_stress_update_many_users():
    """
    This stress test creates multiple users and performs many updates
    to ensure the Client handles repeated write operations under load.
    """
    mock_db = MockDBConnection()
    client = Client(mock_db)

    # Insert users
    for i in range(500):
        client.add_user(f"user{i}", 20)

    # Update them under stress
    for i in range(500):
        client.update_user_age(f"user{i}", 30)

    # Check random sample
    assert client.get_user("user100")["age"] == 30
    assert client.get_user("user400")["age"] == 30


# Stress Test 3
def test_stress_mixed_operations():
    """
    This stress test mixes inserts, updates, and fetches at scale
    to simulate a realistic high-load workflow.
    """
    mock_db = MockDBConnection()
    client = Client(mock_db)

    for i in range(300):
        client.add_user(f"user{i}", i)

    for i in range(300):
        client.update_user_age(f"user{i}", i + 10)
        _ = client.get_user(f"user{i}")

    # Final verification
    assert client.get_user("user250")["age"] == 260


# Stress Test 4
def test_stress_nonexistent_user_queries():
    """
    This stress test performs many queries for users that do not exist
    to ensure the Client does not fail or slow down under invalid requests.
    """
    mock_db = MockDBConnection()
    client = Client(mock_db)

    results = []
    for i in range(1000):
        results.append(client.get_user(f"ghost{i}"))

    # All should be None
    assert all(r is None for r in results)
