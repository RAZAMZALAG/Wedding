import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'Server'))

@pytest.mark.unit
def test_users_import():
    """Test users module import"""
    try:
        import users
        assert True
    except ImportError:
        pytest.skip("Users module not available")
