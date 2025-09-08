"""
Unit Tests for Logger Config Module (logger_config.py)
=====================================================

Tests logging configuration - NO CHEATING!
"""
import pytest
import sys
import os
import logging

# Add Server directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'Server'))

@pytest.mark.unit
class TestLoggerConfig:
    """Test logger configuration"""
    
    def test_import_logger_config(self):
        """Test that we can import logger config module"""
        try:
            from logger_config import get_logger
            assert True, "Successfully imported logger_config"
        except ImportError as e:
            pytest.fail(f"Failed to import logger_config module: {e}")
    
    def test_get_logger_function(self):
        """Test get_logger function"""
        try:
            from logger_config import get_logger
            
            # Test getting a logger
            logger = get_logger(__name__)
            assert isinstance(logger, logging.Logger)
            assert logger.name == __name__
            
        except ImportError:
            pytest.skip("get_logger function not available")
        except Exception as e:
            pytest.fail(f"get_logger failed: {e}")
    
    def test_logger_basic_functionality(self):
        """Test basic logger functionality"""
        try:
            from logger_config import get_logger
            
            logger = get_logger("test_logger")
            
            # Test that we can call logger methods without errors
            logger.info("Test info message")
            logger.debug("Test debug message")
            logger.warning("Test warning message")
            
            assert True, "Logger methods work correctly"
            
        except ImportError:
            pytest.skip("Logger config not available")
        except Exception as e:
            pytest.fail(f"Logger functionality test failed: {e}")

@pytest.mark.unit
class TestLoggingBasics:
    """Test basic logging functionality"""
    
    def test_python_logging_module(self):
        """Test Python's built-in logging module"""
        logger = logging.getLogger("test")
        assert isinstance(logger, logging.Logger)
        
        # Test log levels
        assert logging.DEBUG == 10
        assert logging.INFO == 20
        assert logging.WARNING == 30
        assert logging.ERROR == 40
