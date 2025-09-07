import pytest
from unittest.mock import patch, MagicMock
from Server.auth import allowed_file
from Server.users import serialize_user_data
from Server.models import User

# --------------------------
# Test 1: allowed_file function
# --------------------------
def test_allowed_file_valid_extensions():
    assert allowed_file("photo.png") is True
    assert allowed_file("document.jpg") is True
    assert allowed_file("scan.jpeg") is True
    assert allowed_file("file.pdf") is True

def test_allowed_file_invalid_extensions():
    assert allowed_file("script.js") is False
    assert allowed_file("image.bmp") is False
    assert allowed_file("archive.zip") is False
    assert allowed_file("") is False

# --------------------------
# Test 2: serialize_user_data function
# --------------------------
def test_serialize_user_data_basic():
    user_dict = {
        "_id": "123",
        "first_name": "Linoy",
        "last_name": "Cohen",
        "email": "linoy@example.com",
        "phone_number": "0501234567",
        "location": "Tel Aviv",
        "permission": 3,
        "blocked": False,
        "verified": True,
        "agreement": True
    }
    result = serialize_user_data(user_dict)
    assert result["id"] == "123"
    assert result["first_name"] == "Linoy"
    assert result["last_name"] == "Cohen"
    assert result["email"] == "linoy@example.com"
    assert result["blocked"] is False
    assert result["verified"] is True

# --------------------------
# Test 3: User password hashing and checking
# --------------------------
def test_user_password_hash_and_check():
    user = User(email="test@example.com")
    user.make_password("my_secret")
    assert user.check_password("my_secret") is True
    assert user.check_password("wrong_password") is False

# --------------------------
# Test 4: get_user_by_email uses find_one
# --------------------------
@patch("Server.models.User.find_one")
def test_get_user_by_email_mocked(mock_find):
    mock_find.return_value = User(email="mock@example.com")
    user = User.get_user_by_email("mock@example.com")
    assert user.email == "mock@example.com"
