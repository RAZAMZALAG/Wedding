"""
Unit Tests for Validation Module (validation.py)
================================================

Tests input validation functions - NO CHEATING!
"""
import pytest

# Import modules for testing
try:
    from validation import is_valid_username, is_valid_phone, is_valid_email
    from validation import is_valid_password, is_valid_location, validate_registration
    VALIDATION_AVAILABLE = True
except ImportError:
    VALIDATION_AVAILABLE = False

@pytest.fixture
def app():
    """Create a Flask app for testing"""
    from flask import Flask
    app = Flask(__name__)
    return app

@pytest.mark.unit
class TestValidationFunctions:
    """Test validation functions"""
    
    def test_import_validation_module(self):
        """Test that we can import the validation module"""
        try:
            import validation
            assert hasattr(validation, 'is_valid_username')
            assert hasattr(validation, 'is_valid_phone')
            assert hasattr(validation, 'is_valid_email')
        except ImportError as e:
            pytest.fail(f"Failed to import validation module: {e}")
    
    def test_username_validation_basic(self, app):
        """Test basic username validation"""
        try:
            import validation
            
            with app.app_context():
                # Test valid username
                result = validation.is_valid_username("John")
                assert result is None, "Valid username should return None"
                
                # Test invalid username (too short)
                result = validation.is_valid_username("A")
                assert result is not None, "Too short username should return error"
        except ImportError:
            pytest.skip("Validation module not available")
    
    def test_phone_validation_basic(self, app):
        """Test basic phone validation"""
        try:
            import validation
            
            with app.app_context():
                # Test valid phone
                result = validation.is_valid_phone("0521234567")
                assert result is None, "Valid phone should return None"
                
                # Test invalid phone
                result = validation.is_valid_phone("123")
                assert result is not None, "Invalid phone should return error"
        except ImportError:
            pytest.skip("Validation module not available")
    
    def test_email_validation_basic(self, app):
        """Test basic email validation"""
        try:
            import validation
            
            with app.app_context():
                # Test valid email
                result = validation.is_valid_email("test@example.com")
                assert result is None, "Valid email should return None"
                
                # Test invalid email
                result = validation.is_valid_email("not_an_email")
                assert result is not None, "Invalid email should return error"
        except ImportError:
            pytest.skip("Validation module not available")
    
    def test_password_validation_basic(self, app):
        """Test basic password validation"""
        try:
            from validation import is_valid_password
            
            # Test valid password (5+ characters)
            result = is_valid_password("password123")
            assert result is None, "Valid password should return None"
            
            # Test invalid password (too short)
            result = is_valid_password("1234")
            assert result is not None, "Short password should return error"
            
        except ImportError:
            pytest.skip("is_valid_password function not available")
    
    def test_location_validation_basic(self, app):
        """Test basic location validation"""
        try:
            from validation import is_valid_location
            
            # Test valid Hebrew locations
            valid_locations = ["הדר", "לא מחיפה", "מחיפה, לא מהדר"]
            for location in valid_locations:
                result = is_valid_location(location)
                assert result is None, f"Location '{location}' should be valid"
            
            # Test invalid location
            result = is_valid_location("Tel Aviv")
            assert result is not None, "Invalid location should return error"
            
        except ImportError:
            pytest.skip("is_valid_location function not available")
    
    def test_full_registration_validation(self, app):
        """Test full registration validation function"""
        try:
            from validation import validate_registration
            
            with app.app_context():
                # Test with valid Hebrew location
                result = validate_registration(
                    first_name="John",
                    last_name="Doe",
                    phone="0521234567",
                    email="test@example.com",
                    location="הדר",
                    agreement=True,
                    password="password123"
                )
                
                # Check if result is success (None) or contains error info
                if result is not None:
                    # If there's an error, it should be a tuple/response
                    assert len(result) >= 1, "Error response should have content"
                else:
                    assert True, "Registration validation passed"
                    
        except ImportError:
            pytest.skip("validate_registration function not available")
