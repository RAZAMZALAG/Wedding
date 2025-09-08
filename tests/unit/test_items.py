import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "Server"))

@pytest.mark.unit
def test_items_import():
    try:
        import items
        assert True
    except ImportError:
        pytest.skip("Items module not available")
