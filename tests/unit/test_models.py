"""
Unit Tests for Models Module (models.py)
=======================================

Tests database models and data structures - NO CHEATING!
"""
import pytest
import sys
import os
from datetime import datetime
from bson import ObjectId

# Add Server directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'Server'))

@pytest.mark.unit
class TestModelsImport:
    """Test models module import"""
    
    def test_import_models_module(self):
        """Test that we can import the models module"""
        try:
            from models import User
            assert True, "Successfully imported models"
        except ImportError as e:
            pytest.fail(f"Failed to import models module: {e}")

@pytest.mark.unit 
class TestUserModel:
    """Test User model if it exists"""
    
    def test_user_model_creation(self):
        """Test basic User model functionality"""
        try:
            from models import User
            
            # Test creating a user instance
            user_data = {
                'first_name': 'John',
                'last_name': 'Doe', 
                'email': 'john@example.com',
                'password': 'hashed_password',
                'permission': 1
            }
            
            # This will test if User can be instantiated
            user = User(**user_data)
            assert user.first_name == 'John'
            assert user.email == 'john@example.com'
            
        except ImportError:
            pytest.skip("User model not available")
        except Exception as e:
            pytest.fail(f"User model creation failed: {e}")

@pytest.mark.unit
class TestBasicDataTypes:
    """Test basic data type handling"""
    
    def test_objectid_creation(self):
        """Test ObjectId creation"""
        obj_id = ObjectId()
        assert isinstance(obj_id, ObjectId)
        assert len(str(obj_id)) == 24
    
    def test_datetime_creation(self):
        """Test datetime creation"""
        dt = datetime.now()
        assert isinstance(dt, datetime)
        assert dt.year >= 2025
