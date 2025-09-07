import os
import pytest
from client2 import Client
from test_client2_ForStudents import MockDBConnection

# Get the path to the current directory to ensure files are always found
current_dir = os.path.dirname(__file__)

# Integration Test 1
def test_client_inserts_and_fetches_data():
    """
    This integration test checks if the Client can insert a record into the database
    and then fetch it successfully, simulating a full flow with the mocked DB.
    """
    mock_db = MockDBConnection()
    client = Client(mock_db)
    
    client.add_user("Alice", 30)
    result = client.get_user("Alice")
    
    assert result == {"name": "Alice", "age": 30}


# Integration Test 2
def test_client_updates_data_flow():
    """
    This integration test ensures the Client can update a record and the changes
    are reflected when fetching the data.
    """
    mock_db = MockDBConnection()
    client = Client(mock_db)
    
    client.add_user("Bob", 25)
    client.update_user_age("Bob", 26)
    
    result = client.get_user("Bob")
    assert result["age"] == 26


# Integration Test 3
def test_client_handles_nonexistent_user():
    """
    This integration test validates the Client's behavior when fetching a user
    that does not exist in the database.
    """
    mock_db = MockDBConnection()
    client = Client(mock_db)
    
    result = client.get_user("Charlie")
    assert result is None


# Integration Test 4
def test_client_multiple_operations():
    """
    This integration test simulates multiple operations: adding, updating,
    and fetching multiple users to test overall integration.
    """
    mock_db = MockDBConnection()
    client = Client(mock_db)
    
    client.add_user("David", 40)
    client.add_user("Eve", 35)
    client.update_user_age("David", 41)
    
    david = client.get_user("David")
    eve = client.get_user("Eve")
    
    assert david["age"] == 41
    assert eve["age"] == 35
