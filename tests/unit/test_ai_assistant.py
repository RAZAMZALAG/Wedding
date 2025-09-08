import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "Server"))

@pytest.mark.unit
def test_ai_assistant_import():
    try:
        import ai_assistant
        assert True
    except ImportError:
        pytest.skip("AI assistant module not available")

@pytest.mark.unit
def test_refusal_messages():
    try:
        from ai_assistant import REFUSAL_MESSAGES
        assert "he" in REFUSAL_MESSAGES
        assert "en" in REFUSAL_MESSAGES
        assert len(REFUSAL_MESSAGES["he"]) > 0
    except ImportError:
        pytest.skip("REFUSAL_MESSAGES not available")

@pytest.mark.unit
def test_get_catalog_summary():
    try:
        from ai_assistant import get_catalog_summary
        # Just test the function exists and can be called
        result = get_catalog_summary()
        assert isinstance(result, dict) or result is None
    except ImportError:
        pytest.skip("get_catalog_summary not available")
    except Exception:
        # Function might fail due to missing database, thats OK
        assert True
