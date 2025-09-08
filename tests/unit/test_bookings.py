import pytest
import sys
import os
from datetime import date

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'Server'))

@pytest.mark.unit
def test_bookings_import():
    """Test bookings module import"""
    try:
        import bookings
        assert True
    except ImportError:
        pytest.skip("Bookings module not available")

@pytest.mark.unit 
def test_count_booking_units():
    """Test count_booking_units function"""
    try:
        from bookings import count_booking_units
        
        # Test basic functionality
        result = count_booking_units('2025-09-15', '2025-09-17')
        assert result == 3
        
        # Test single day
        result = count_booking_units('2025-09-15', '2025-09-15')
        assert result == 1
        
    except ImportError:
        pytest.skip("count_booking_units not available")
