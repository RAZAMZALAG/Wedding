import sys
import os

# מוסיפים את תיקיית Server ל־sys.path כדי ש־auth.py ימצא את models
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'Server')))
import unittest
from unittest.mock import patch, MagicMock
from io import BytesIO
from flask import Flask
from Server.auth import auth_bp, login_user, register_user, verify_email
from Server.models import User

# להוסיף את תיקיית ה־Server ל־sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

class TestAuthUnit(unittest.TestCase):

    def setUp(self):
        # יצירת Flask test client
        self.app = Flask(__name__)
        self.app.register_blueprint(auth_bp)
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()

        # dummy user למספר בדיקות
        self.dummy_user = User(
            _id='123',
            first_name='Test',
            last_name='User',
            phone_number='123456',
            email='test@test.com',
            location='TLV',
            agreement=True,
            id_file=b'filebytes'
        )
        self.dummy_user.verified = True
        self.dummy_user.permission = 'user'
        self.dummy_user.check_password = lambda x: x == 'correctpass'

    # ------------------------
    # Test login with invalid password
    # ------------------------
    def test_login_invalid_credentials(self):
        with patch.object(User, 'get_user_by_email', return_value=self.dummy_user):
            response = self.client.post('/login', json={'email': 'test@test.com', 'password': 'wrongpass'})
            self.assertEqual(response.status_code, 400)
            self.assertIn(b'INVALID_CREDENTIALS', response.data)

    # ------------------------
    # Test login with correct credentials
    # ------------------------
    def test_login_success(self):
        with patch.object(User, 'get_user_by_email', return_value=self.dummy_user):
            response = self.client.post('/login', json={'email': 'test@test.com', 'password': 'correctpass'})
            self.assertEqual(response.status_code, 200)
            self.assertIn(b'token', response.data)

    # ------------------------
    # Test login with unverified email
    # ------------------------
    def test_login_unverified_email(self):
        unverified_user = self.dummy_user
        unverified_user.verified = False
        with patch.object(User, 'get_user_by_email', return_value=unverified_user):
            response = self.client.post('/login', json={'email': 'test@test.com', 'password': 'correctpass'})
            self.assertEqual(response.status_code, 403)
            self.assertIn(b'EMAIL_NOT_VERIFIED', response.data)

    # ------------------------
    # Test registration success
    # ------------------------
    def test_register_success(self):
        with patch.object(User, 'get_user_by_email', return_value=None):
            with patch.object(User, 'save', return_value=None):
                data = {
                    'firstName': 'Test',
                    'lastName': 'User',
                    'phone': '123456',
                    'email': 'test@test.com',
                    'location': 'TLV',
                    'agreement': 'true',
                    'password': 'pass123',
                    'file': (BytesIO(b'filebytes'), 'id.png')
                }
                response = self.client.post('/register', data=data, content_type='multipart/form-data')
                self.assertEqual(response.status_code, 201)
                self.assertIn(b'USER_CREATED', response.data)

    # ------------------------
    # Test verify email success
    # ------------------------
    def test_verify_email_success(self):
        dummy_user = self.dummy_user
        with patch.object(User, 'get_user_by_email', return_value=dummy_user):
            with patch.object(User, 'save', return_value=None):
                # יצירת token דמה
                from flask_jwt_extended import create_access_token
                token = create_access_token(identity=dummy_user.email, additional_claims={"email_verification": True})
                response = self.client.get(f'/verify-email?token={token}')
                self.assertEqual(response.status_code, 200)
                self.assertIn('האימות הושלם בהצלחה'.encode('utf-8'), response.data)


if __name__ == '__main__':
    unittest.main()
