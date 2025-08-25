from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
from extensions import db, jwt
from auth import auth_bp
from users import user_bp
from items import item_bp
from bookings import booking_bp
from ai_assistant import ai_bp
from models import User
from dotenv import load_dotenv
from apscheduler.schedulers.background import BackgroundScheduler
from bookings import send_booking_return_reminders
import atexit, os

load_dotenv()


def create_app():
    app = Flask(__name__, static_folder='dist')
    CORS(app)
    app.config.from_prefixed_env()
    env = os.getenv("ENV")
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DEV_DB_URI") if env != "PROD" else os.getenv("PROD_DB_URI")

    # init extensions
    db.init_app(app)
    jwt.init_app(app)

    # API requests

    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(user_bp, url_prefix="/api/users")
    app.register_blueprint(item_bp, url_prefix="/api/items")
    app.register_blueprint(booking_bp, url_prefix="/api/bookings")
    app.register_blueprint(ai_bp, url_prefix="/api/ai")

    @jwt.user_lookup_loader
    def user_lookup_callback(jwt_headers, jwt_data):
        identity = jwt_data['sub']
        return User.query.filter_by(email=identity).one_or_none()

    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_data):
        return jsonify({"error": "TOKEN_EXPIRED"}), 401

    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return jsonify({"error": "INVALID_TOKEN"}), 401

    @jwt.unauthorized_loader
    def missing_token_callback(error):
        return jsonify({"error": "MISSING_TOKEN"}), 401

    # Static files serving (for post build environment)

    @app.route('/', methods=['GET'])
    def serve_static():
        return send_from_directory(app.static_folder, 'index.html')

    @app.route('/<path:path>')
    def serve_static_files(path):
        if "." in path:  # static files
            return send_from_directory(os.path.join(app.static_folder), path)
        return send_from_directory(app.static_folder, 'index.html')

    # Scheduler for sending booking return reminders
    def scheduled_send_booking_return_reminders():
        with app.app_context():
            send_booking_return_reminders()

    scheduler = BackgroundScheduler()
    scheduler.add_job(func=scheduled_send_booking_return_reminders, trigger='cron', hour=9)
    scheduler.start()
    
    # Initialize database tables
    with app.app_context():
        db.create_all()
        # Only send reminders after database is initialized
        try:
            send_booking_return_reminders()
        except Exception as e:
            print(f"Warning: Could not send initial reminders: {e}")
            
    atexit.register(lambda: scheduler.shutdown())
    return app


if __name__ == "__main__":
    application = create_app()
    application.run(host='0.0.0.0', port=os.getenv("PORT"))
