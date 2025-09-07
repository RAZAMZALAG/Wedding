import pytest

# Mock DB class
class MockDBConnection:
    def __init__(self):
        self.data = {}

    def insert_user(self, name, age):
        self.data[name] = {"name": name, "age": age}

    def fetch_user(self, name):
        return self.data.get(name)

    def update_user(self, name, age):
        if name in self.data:
            self.data[name]["age"] = age


# Mock Client class
class Client:
    def __init__(self, db):
        self.db = db

    def add_user(self, name, age):
        self.db.insert_user(name, age)

    def get_user(self, name):
        return self.db.fetch_user(name)

    def update_user_age(self, name, age):
        self.db.update_user(name, age)


# Integration Test 1
def test_client_inserts_and_fetches_data():
    mock_db = MockDBConnection()
    client = Client(mock_db)
    
    client.add_user("Alice", 30)
    result = client.get_user("Alice")
    assert result == {"name": "Alice", "age": 30}


# Integration Test 2
def test_client_updates_data_flow():
    mock_db = MockDBConnection()
    client = Client(mock_db)
    
    client.add_user("Bob", 25)
    client.update_user_age("Bob", 26)
    result = client.get_user("Bob")
    assert result["age"] == 26


# Integration Test 3
def test_client_handles_nonexistent_user():
    mock_db = MockDBConnection()
    client = Client(mock_db)
    
    result = client.get_user("Charlie")
    assert result is None


# Integration Test 4
def test_client_multiple_operations():
    mock_db = MockDBConnection()
    client = Client(mock_db)
    
    client.add_user("David", 40)
    client.add_user("Eve", 35)
    client.update_user_age("David", 41)
    
    david = client.get_user("David")
    eve = client.get_user("Eve")
    
    assert david["age"] == 41
    assert eve["age"] == 35
