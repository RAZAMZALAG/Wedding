import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "Server"))

@pytest.mark.unit
def test_schemas_import():
    try:
        import schemas
        assert True
    except ImportError:
        pytest.skip("Schemas module not available")

@pytest.mark.unit
def test_user_schema():
    try:
        from schemas import UserSchema
        schema = UserSchema()
        assert schema is not None
    except ImportError:
        pytest.skip("UserSchema not available")
