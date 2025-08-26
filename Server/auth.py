from flask import Blueprint, jsonify, request, render_template_string, redirect
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, current_user, decode_token
from models import User
from datetime import timedelta
from validation import validate_registration
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email_utils import send_verification_email  
import uuid
import os


auth_bp = Blueprint("auth", __name__)


def create_jwt(identity, permission):
    return create_access_token(identity,
                               expires_delta=timedelta(minutes=30),
                               additional_claims={"permission": permission})


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg', 'pdf'}


@auth_bp.post('/register')
def register_user():
    if 'file' not in request.files:
        return jsonify({'error': 'ID REQUIRED'}), 400

    file = request.files['file']
    if not file or not allowed_file(file.filename):
        return jsonify({'error': 'BAD ID FILE TYPE'}), 400
    id_file = file.read()

    first_name = request.form.get('firstName')
    last_name = request.form.get('lastName')
    phone = request.form.get('phone')
    email = request.form.get('email')
    location = request.form.get('location')
    agreement = request.form.get('agreement') == 'true'
    password = request.form.get('password')

    error = validate_registration(first_name, last_name, phone, email, location, agreement, password)
    if error:
        return error

    user = User.get_user_by_email(email=email)
    if user:
        return jsonify({"error": "USER_EXISTS"}), 400

    new_user = User(
        _id=str(uuid.uuid4()),
        first_name=first_name,
        last_name=last_name,
        phone_number=phone,
        email=email,
        location=location,
        agreement=agreement,
        id_file=id_file
    )
    new_user.make_password(password)
    new_user.save()

    verification_token = create_access_token(
        identity=email,
        expires_delta=timedelta(hours=24),
        additional_claims={"email_verification": True}
    )

    send_verification_email(email, first_name, verification_token)

    return jsonify({"message": "USER_CREATED"}), 201

from flask import render_template_string, redirect
from flask import request, jsonify, render_template_string
from flask_jwt_extended import decode_token

@auth_bp.get("/verify-email")
def verify_email():
    token = request.args.get("token")
    if not token:
        return jsonify({"error": "NO_TOKEN_PROVIDED"}), 400

    try:
        decoded = decode_token(token)
        email = decoded["sub"]
        if not decoded.get("email_verification"):
            return jsonify({"error": "INVALID_VERIFICATION_TOKEN"}), 400
    except Exception:
        return jsonify({"error": "INVALID_OR_EXPIRED_TOKEN"}), 400

    user = User.get_user_by_email(email)
    if not user:
        return jsonify({"error": "USER_NOT_FOUND"}), 404

    if user.verified:
        client_url = os.getenv("CLIENT_URL", "http://localhost:5173")
        return render_template_string("""
        <html dir="rtl" lang="he">
          <head>
            <meta charset="UTF-8">
            <title>כתובת כבר אומתה</title>
          </head>
          <body style="text-align:center; font-family:Arial; margin-top:50px;">
            <h2>✅ כתובת הדוא"ל שלך כבר אומתה בעבר.</h2>
            <p>באפשרותך <a href="{{ client_url }}/login">להתחבר</a> לאתר Wedding Dreams 💒</p>
          </body>
        </html>
        """, client_url=client_url)

    # עדכון סטטוס האימות ושמירה
    user.verified = True
    user.save()

    client_url = os.getenv("CLIENT_URL", "http://localhost:5173")
    return render_template_string("""
    <html dir="rtl" lang="he">
      <head>
        <meta charset="UTF-8">
        <title>האימות הושלם</title>
      </head>
      <body style="text-align:center; font-family:Arial; margin-top:50px;">
        <h2>✅ האימות הושלם בהצלחה!</h2>
        <p>כעת באפשרותך <a href="{{ client_url }}/login">להתחבר</a> לאתר Wedding Dreams 💒</p>
      </body>
    </html>
    """, client_url=client_url)




@auth_bp.post('/login')
def login_user():
    data = request.get_json()
    user = User.get_user_by_email(email=data.get('email'))

    if user and user.check_password(data.get('password')):
        if not user.verified:
            return jsonify({"error": "EMAIL_NOT_VERIFIED"}), 403

        access_token = create_jwt(user.email, user.permission)
        refresh_token = create_refresh_token(user.email, expires_delta=timedelta(days=1))
        user_name = f"{user.first_name} {user.last_name}"
        return jsonify({"token": access_token, "refresh": refresh_token, 
                        "permission": user.permission, "user_name": user_name}), 200

    return jsonify({"error": "INVALID_CREDENTIALS"}), 400


@auth_bp.get('/whoami')
@jwt_required()
def get_current_user_details():
    return jsonify({"email": current_user.email}), 200


@auth_bp.post('/refresh')
@jwt_required(refresh=True)
def refresh_token():
    user = current_user
    token = create_jwt(user.email, user.permission)
    return jsonify({"token": token}), 200