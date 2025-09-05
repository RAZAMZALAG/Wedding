from flask import Flask, jsonify, send_from_directory, request, g
from flask_cors import CORS
from extensions import mongo, jwt
from auth import auth_bp
from users import user_bp, CustomJSONEncoder
from items import item_bp
from bookings import booking_bp
from ai_assistant import ai_bp
from models import User, TemporaryLock, init_db
from dotenv import load_dotenv
from apscheduler.schedulers.background import BackgroundScheduler
from bookings import send_booking_return_reminders
from logger_config import init_app_logging, get_logger, log_request_response, PerformanceMonitor
import atexit, os, uuid, time

load_dotenv()


def create_app():
    app = Flask(__name__, static_folder='dist')
    
    # Initialize logging first
    init_app_logging(app)
    logger = get_logger('app')
    
    CORS(app)
    app.config.from_prefixed_env()
    env = os.getenv("ENV")
    
    logger.info(f"Creating Flask application in {env or 'development'} environment")
    
    # Set custom JSON encoder
    app.json_encoder = CustomJSONEncoder
    
    # JWT Configuration
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key-for-development')
    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'your-jwt-secret-key')
    
    # MongoDB Configuration
    mongo_uri = os.getenv("MONGO_URI") or os.getenv("DEV_MONGO_URI") if env != "PROD" else os.getenv("PROD_MONGO_URI")
    app.config["MONGO_URI"] = mongo_uri or "mongodb://localhost:27017/wedding_planner"
    
    logger.info(f"MongoDB URI configured: {app.config['MONGO_URI'].replace('://','://*****@').split('@')[-1] if '@' in app.config['MONGO_URI'] else app.config['MONGO_URI']}")

    # init extensions
    with PerformanceMonitor("MongoDB and JWT initialization"):
        mongo.init_app(app)
        jwt.init_app(app)
    
    # Add request ID middleware
    @app.before_request
    def before_request():
        g.request_id = str(uuid.uuid4())
        g.start_time = time.time()
    
    # Add response logging middleware
    @app.after_request
    def after_request(response):
        if hasattr(g, 'start_time'):
            duration_ms = (time.time() - g.start_time) * 1000
            logger.info(
                f"Request completed: {request.method} {request.path} - {response.status_code} in {duration_ms:.2f}ms",
                extra={'extra_data': {
                    'request_id': g.request_id,
                    'method': request.method,
                    'path': request.path,
                    'status_code': response.status_code,
                    'duration_ms': duration_ms,
                    'content_length': response.content_length,
                    'remote_addr': request.remote_addr
                }}
            )
        return response

    # API requests
    logger.info("Registering API blueprints")
    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(user_bp, url_prefix="/api/users")
    app.register_blueprint(item_bp, url_prefix="/api/items")
    app.register_blueprint(booking_bp, url_prefix="/api/bookings")
    app.register_blueprint(ai_bp, url_prefix="/api/ai")

    @jwt.user_lookup_loader
    def user_lookup_callback(jwt_headers, jwt_data):
        identity = jwt_data['sub']
        user = User.get_user_by_email(identity)
        if user:
            g.user_id = str(user._id)
            g.user_email = user.email
        return user

    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_data):
        logger.warning(f"Expired token access attempt: {jwt_data.get('sub', 'unknown')}")
        return jsonify({"error": "TOKEN_EXPIRED"}), 401

    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        logger.warning(f"Invalid token access attempt: {error}")
        return jsonify({"error": "INVALID_TOKEN"}), 401

    @jwt.unauthorized_loader
    def missing_token_callback(error):
        logger.info(f"Unauthorized access attempt to {request.path}")
        return jsonify({"error": "MISSING_TOKEN"}), 401

    # Global error handler
    @app.errorhandler(Exception)
    def handle_exception(e):
        logger.error(
            f"Unhandled exception in {request.method} {request.path}",
            exc_info=True,
            extra={'extra_data': {
                'request_id': getattr(g, 'request_id', 'unknown'),
                'method': request.method,
                'path': request.path,
                'remote_addr': request.remote_addr,
                'error_type': type(e).__name__
            }}
        )
        
        # Don't leak internal errors in production
        if os.getenv('FLASK_ENV') == 'production':
            return jsonify({"error": "Internal server error"}), 500
        else:
            return jsonify({"error": str(e)}), 500

    # Static files serving (for post build environment)

    @app.route('/catalog/<filename>')
    def serve_catalog_image(filename):
        catalog_dir = os.path.join(os.path.dirname(__file__), 'catalog')
        return send_from_directory(catalog_dir, filename)

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
            logger.info("Running scheduled booking return reminders")
            try:
                send_booking_return_reminders()
                logger.info("Scheduled booking return reminders completed successfully")
            except Exception as e:
                logger.error("Error in scheduled booking return reminders", exc_info=True)

    def cleanup_expired_temporary_locks():
        with app.app_context():
            logger.info("Running cleanup of expired temporary locks")
            try:
                TemporaryLock.cleanup_expired_locks()
                logger.info("Cleanup of expired temporary locks completed successfully")
            except Exception as e:
                logger.error("Error in cleanup of expired temporary locks", exc_info=True)

    logger.info("Setting up background scheduler for booking reminders and lock cleanup")
    scheduler = BackgroundScheduler()
    scheduler.add_job(func=scheduled_send_booking_return_reminders, trigger='cron', hour=9)
    # Clean up expired locks every 10 minutes
    scheduler.add_job(func=cleanup_expired_temporary_locks, trigger='interval', minutes=10)
    scheduler.start()
    
    # Initialize database and collections
    logger.info("Initializing database and collections")
    with app.app_context():
        with PerformanceMonitor("Database initialization"):
            init_db()
        
        # Only send reminders after database is initialized
        try:
            logger.info("Sending initial booking return reminders")
            send_booking_return_reminders()
        except Exception as e:
            logger.warning(f"Could not send initial reminders: {e}")
            
    atexit.register(lambda: scheduler.shutdown())
    
    logger.info("Flask application created successfully")
    return app


if __name__ == "__main__":
    application = create_app()
    logger = get_logger('main')
    port = os.getenv("PORT", 5000)
    
    logger.info(f"Starting Wedding Planner application on port {port}")
    application.run(host='0.0.0.0', port=port, debug=os.getenv('FLASK_ENV') != 'production')


# For gunicorn
app = create_app()
