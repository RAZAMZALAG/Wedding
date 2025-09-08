"""
Pytest configuration file for the Wedding Planner project
"""
import pytest
import sys
import os
from flask import Flask
from flask_jwt_extended import JWTManager

# Add the Server directory to Python path for imports
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
server_path = os.path.join(project_root, 'Server')
if server_path not in sys.path:
    sys.path.insert(0, server_path)

@pytest.fixture(scope="session")
def app():
    """Create a Flask app for testing"""
    app = Flask(__name__)
    app.config['JWT_SECRET_KEY'] = 'test_jwt_secret_key'
    app.config['TESTING'] = True
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = False
    jwt = JWTManager(app)
    return app

@pytest.fixture(scope="session")
def app_context(app):
    """Create Flask app context for tests that need it"""
    with app.app_context():
        yield app

@pytest.fixture(scope="session")
def integration_app():
    """Create Flask app specifically for integration tests"""
    from main import create_app
    app = create_app()
    app.config['TESTING'] = True
    app.config['JWT_SECRET_KEY'] = 'integration_test_jwt_secret'
    app.config['WTF_CSRF_ENABLED'] = False
    return app

@pytest.fixture(scope="session")
def integration_client(integration_app):
    """Create test client for integration tests"""
    return integration_app.test_client()
