# tests/test_security.py
import pytest

# ---------------------------
# Mock DB and Client Classes
# ---------------------------

class MockDBConnection:
    """A simple mock database connection."""
    def __init__(self):
        self.data = {}
    
    def insert(self, key, value):
        self.data[key] = value
    
    def get(self, key):
        return self.data.get(key)
    
    def update(self, key, value):
        if key in self.data:
            self.data[key] = value


class Client:
    """A mock client to simulate user operations."""
    def __init__(self, db):
        self.db = db
        self.logged_in = False
    
    def login(self, username, password):
        # For testing, any username/password combination works
        self.logged_in = True
    
    def logout(self):
        self.logged_in = False
    
    def add_user(self, name, age):
        if not self.logged_in:
            raise PermissionError("User must be logged in to add users")
        self.db.insert(name, {"name": name, "age": age})
    
    def get_user(self, name):
        return self.db.get(name)
    
    def update_user_age(self, name, age):
        if not self.logged_in:
            raise PermissionError("User must be logged in to update users")
        self.db.update(name, {"name": name, "age": age})


# ---------------------------
# Security Test Cases
# ---------------------------

def test_add_user_requires_login():
    db = MockDBConnection()
    client = Client(db)
    
    # Not logged in
    with pytest.raises(PermissionError):
        client.add_user("Alice", 30)
    
    # After login
    client.login("admin", "password")
    client.add_user("Alice", 30)
    result = client.get_user("Alice")
    assert result == {"name": "Alice", "age": 30}


def test_update_user_requires_login():
    db = MockDBConnection()
    client = Client(db)
    
    client.login("admin", "password")
    client.add_user("Bob", 25)
    client.logout()
    
    # Trying to update while logged out should raise error
    with pytest.raises(PermissionError):
        client.update_user_age("Bob", 26)
    
    # Login again to update successfully
    client.login("admin", "password")
    client.update_user_age("Bob", 26)
    result = client.get_user("Bob")
    assert result["age"] == 26


def test_fetch_nonexistent_user():
    db = MockDBConnection()
    client = Client(db)
    
    result = client.get_user("Ghost")
    assert result is None


def test_multiple_operations_with_login():
    db = MockDBConnection()
    client = Client(db)
    
    client.login("admin", "password")
    
    # Add multiple users
    client.add_user("David", 40)
    client.add_user("Eve", 35)
    
    # Update one user
    client.update_user_age("David", 41)
    
    david = client.get_user("David")
    eve = client.get_user("Eve")
    
    assert david["age"] == 41
    assert eve["age"] == 35
