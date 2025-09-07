import pytest

# --------------------------
# Mock Client & DB
# --------------------------
class MockDBConnection:
    def __init__(self):
        self.users = {}

class Client:
    def __init__(self, db):
        self.db = db

    def add_user(self, username, age):
        self.db.users[username] = {"age": age}

    def update_user_age(self, username, age):
        if username in self.db.users:
            self.db.users[username]["age"] = age

    def get_user(self, username):
        return self.db.users.get(username)


# --------------------------
# Stress Test 1
# --------------------------
def test_stress_insert_many_users():
    mock_db = MockDBConnection()
    client = Client(mock_db)

    for i in range(1000):
        client.add_user(f"user{i}", i % 100)

    result = client.get_user("user999")
    assert result["age"] == 99


# --------------------------
# Stress Test 2
# --------------------------
def test_stress_update_many_users():
    mock_db = MockDBConnection()
    client = Client(mock_db)

    for i in range(500):
        client.add_user(f"user{i}", 20)

    for i in range(500):
        client.update_user_age(f"user{i}", 30)

    assert client.get_user("user100")["age"] == 30
    assert client.get_user("user400")["age"] == 30


# --------------------------
# Stress Test 3
# --------------------------
def test_stress_mixed_operations():
    mock_db = MockDBConnection()
    client = Client(mock_db)

    for i in range(300):
        client.add_user(f"user{i}", i)

    for i in range(300):
        client.update_user_age(f"user{i}", i + 10)
        _ = client.get_user(f"user{i}")

    assert client.get_user("user250")["age"] == 260


# --------------------------
# Stress Test 4
# --------------------------
def test_stress_nonexistent_user_queries():
    mock_db = MockDBConnection()
    client = Client(mock_db)

    results = [client.get_user(f"ghost{i}") for i in range(1000)]
    assert all(r is None for r in results)
