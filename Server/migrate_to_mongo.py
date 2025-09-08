"""
MongoDB Migration and Initial Data Setup
Run this script to migrate data from PostgreSQL to MongoDB
"""

from flask import Flask
from extensions import mongo
from models import User, Category, Item, Cart, Order, init_db
from werkzeug.security import generate_password_hash
import base64
from datetime import datetime, date
import os
from dotenv import load_dotenv

load_dotenv()

def create_app_context():
    """Create Flask app context for database operations"""
    app = Flask(__name__)
    # Use the same logic as main.py for MongoDB URI
    env = os.getenv("ENV", "DEV")
    mongo_uri = os.getenv("MONGO_URI") or os.getenv("DEV_MONGO_URI") if env != "PROD" else os.getenv("PROD_MONGO_URI")
    app.config["MONGO_URI"] = mongo_uri or "mongodb://localhost:27017/wedding_planner"
    mongo.init_app(app)
    return app

def create_admin_user():
    """Create default admin user"""
    try:
        # Check if admin already exists
        admin = User.get_user_by_email("admin@email.com")
        if admin:
            print("Admin user already exists")
            return
        
        # Read a sample image file or create dummy data
        try:
            with open("sample_id.jpg", "rb") as f:
                id_file_data = f.read()
        except FileNotFoundError:
            # Create dummy binary data
            id_file_data = b"dummy_id_file_data"
        
        admin_user = User(
            _id="admin-001",
            email="admin@email.com",
            permission=3,
            first_name="Admin",
            last_name="User",
            phone_number="050-1234567",
            location="Tel Aviv",
            agreement=True,
            blocked=False,
            id_file=id_file_data,
            verified=True
        )
        admin_user.make_password("admin123")
        admin_user.save()
        
        print("Admin user created successfully")
        
    except Exception as e:
        print(f"Error creating admin user: {str(e)}")


def create_sample_user():
    """Create sample regular user"""
    try:
        # Check if user already exists
        user = User.get_user_by_email("user@email.com")
        if user:
            print("Sample user already exists")
        else:
            try:
                with open("sample_id.jpg", "rb") as f:
                    id_file_data = f.read()
            except FileNotFoundError:
                id_file_data = b"dummy_id_file_data"
            
            sample_user = User(
                _id="user-001",
                email="user@email.com",
                permission=1,
                first_name="משה",
                last_name="כהן",
                phone_number="052-9876543",
                location="ירושלים",
                agreement=True,
                blocked=False,
                id_file=id_file_data,
                verified=True
            )
            sample_user.make_password("user123")
            sample_user.save()
            print("Sample user created successfully")
        
        # הוספת משתמשים נוספים
        additional_users = [
            {
                "_id": "user-002",
                "email": "sarah@email.com",
                "first_name": "שרה",
                "last_name": "לוי",
                "phone_number": "054-1234567",
                "location": "תל אביב",
                "password": "sarah123"
            },
            {
                "_id": "user-003", 
                "email": "david@email.com",
                "first_name": "דוד",
                "last_name": "ישראלי",
                "phone_number": "050-9988776",
                "location": "חיפה",
                "password": "david123"
            },
            {
                "_id": "user-004",
                "email": "rachel@email.com", 
                "first_name": "רחל",
                "last_name": "אברהם",
                "phone_number": "053-5566778",
                "location": "באר שבע",
                "password": "rachel123"
            },
            {
                "_id": "user-005",
                "email": "yoni@email.com",
                "first_name": "יוני",
                "last_name": "רוזן",
                "phone_number": "052-3344556",
                "location": "נתניה",
                "password": "yoni123"
            },
            {
                "_id": "user-006",
                "email": "manager@email.com",
                "first_name": "מנהל",
                "last_name": "מערכת",
                "phone_number": "050-1111222",
                "location": "תל אביב",
                "password": "manager123",
                "permission": 2  # הרשאת מנהל
            }
        ]
        
        for user_data in additional_users:
            # Check if user already exists
            existing_user = User.get_user_by_email(user_data["email"])
            if existing_user:
                print(f"User {user_data['email']} already exists")
                continue
                
            try:
                with open("sample_id.jpg", "rb") as f:
                    id_file_data = f.read()
            except FileNotFoundError:
                id_file_data = b"dummy_id_file_data"
            
            new_user = User(
                _id=user_data["_id"],
                email=user_data["email"],
                permission=user_data.get("permission", 1),  # רגיל כברירת מחדל
                first_name=user_data["first_name"],
                last_name=user_data["last_name"],
                phone_number=user_data["phone_number"],
                location=user_data["location"],
                agreement=True,
                blocked=False,
                id_file=id_file_data,
                verified=True
            )
            new_user.make_password(user_data["password"])
            new_user.save()
            print(f"Created user: {user_data['first_name']} {user_data['last_name']} ({user_data['email']})")
        
    except Exception as e:
        print(f"Error creating users: {str(e)}")


def create_sample_items():
    """Create sample wedding items"""
    sample_items = [
        {
            "name": "צלחות חרסינה לבנות",
            "category": "כלי הגשה וחרסינה",
            "total_amount": 100,
            "amount": 100,
            "price": 5.0,
            "notes": "צלחות איכותיות לאירועים",
            "description": "צלחות חרסינה לבנות יפות ואלגנטיות לחתונה",
            "condition": "מעולה",
            "hidden": False,
            "image": "plates.jpg"
        },
        {
            "name": "כיסאות צ'יברי זהב",
            "category": "כיסאות ושולחנות",
            "total_amount": 50,
            "amount": 50,
            "price": 12.0,
            "notes": "כיסאות אלגנטיים לחתונה",
            "description": "כיסאות צ'יברי בצבע זהב, מושלמים לחתונות יוקרה",
            "condition": "מעולה",
            "hidden": False,
            "image": "chiavari_chairs.jpg"
        },
        {
            "name": "זרי פרחים למרכז שולחן",
            "category": "אבזרי נוי ועיצוב",
            "total_amount": 20,
            "amount": 20,
            "price": 45.0,
            "notes": "זרים טריים ויפים",
            "description": "זרי פרחים מיוחדים למרכז השולחן, מעוצבים במיוחד לחתונה",
            "condition": "חדש",
            "hidden": False,
            "image": "centerpieces.jpg"
        },
        {
            "name": "מערכת הגברה מקצועית",
            "category": "ציוד הגברה",
            "total_amount": 5,
            "amount": 5,
            "price": 200.0,
            "notes": "מערכת שמע איכותית לאירועים",
            "description": "מערכת הגברה מקצועית עם מיקרופונים אלחוטיים ורמקולים",
            "condition": "מעולה",
            "hidden": False,
            "image": "sound_system.jpg"
        },
        {
            "name": "תאורת לד צבעונית",
            "category": "ציוד תאורה",
            "total_amount": 10,
            "amount": 10,
            "price": 80.0,
            "notes": "תאורה אטמוספרית לאירוע",
            "description": "מערכת תאורת לד צבעונית ליצירת אווירה רומנטית",
            "condition": "מעולה",
            "hidden": False,
            "image": "led_lighting.jpg"
        },
        # מוצרים חדשים שאני מוסיף
        {
            "name": "שולחנות עגולים לבנים",
            "category": "כיסאות ושולחנות",
            "total_amount": 30,
            "amount": 30,
            "price": 25.0,
            "notes": "שולחנות עגולים ל-8 אנשים",
            "description": "שולחנות עגולים לבנים אלגנטיים, מושלמים לחתונות גדולות",
            "condition": "מעולה",
            "hidden": False,
            "image": "wedding_tables.jpg"
        },
        {
            "name": "כלי כסף מפוארים",
            "category": "כלי הגשה וחרסינה",
            "total_amount": 150,
            "amount": 150,
            "price": 8.0,
            "notes": "סט כלי אכילה מכסף",
            "description": "כלי כסף אלגנטיים למראה יוקרתי בחתונה",
            "condition": "מעולה",
            "hidden": False,
            "image": "silverware.jpg"
        },
        {
            "name": "כוסות קריסטל ליין",
            "category": "כלי הגשה וחרסינה",
            "total_amount": 80,
            "amount": 80,
            "price": 6.0,
            "notes": "כוסות יין מקריסטל איכותי",
            "description": "כוסות קריסטל יפות ליין, מעניקות מגע אלגנטי לשולחן",
            "condition": "מעולה",
            "hidden": False,
            "image": "crystal_glasses.jpg"
        },
        {
            "name": "אוהל גזיבו לחופה",
            "category": "אבזרי נוי ועיצוב",
            "total_amount": 3,
            "amount": 3,
            "price": 300.0,
            "notes": "אוהל יפה לטקס החופה",
            "description": "אוהל גזיבו לבן מפואר לטקס החופה, מעוצב בסגנון רומנטי",
            "condition": "מעולה",
            "hidden": False,
            "image": "wedding_tent.jpg"
        },
        {
            "name": "רחבת פרקט לריקודים",
            "category": "ציוד עזר לאירועים",
            "total_amount": 2,
            "amount": 2,
            "price": 400.0,
            "notes": "רחבת ריקודים מעץ איכותי",
            "description": "רחבת פרקט 6x6 מטר לריקודים, התקנה כלולה",
            "condition": "מעולה",
            "hidden": False,
            "image": "dance_floor.jpg"
        },
        {
            "name": "שטיח אדום VIP",
            "category": "אבזרי נוי ועיצוב",
            "total_amount": 4,
            "amount": 4,
            "price": 50.0,
            "notes": "שטיח אדום לכניסה חגיגית",
            "description": "שטיח אדום אלגנטי ליצירת כניסה VIP לאירוע",
            "condition": "מעולה",
            "hidden": False,
            "image": "red_carpet.jpg"
        },
        {
            "name": "זר כלה קלאסי",
            "category": "הזמנות ומזכרות",
            "total_amount": 10,
            "amount": 10,
            "price": 120.0,
            "notes": "זר כלה מיוחד ויפה",
            "description": "זר כלה קלאסי עם ורדים לבנים ופרחי עונה",
            "condition": "חדש",
            "hidden": False,
            "image": "bridal_bouquet.jpg"
        },
        {
            "name": "עמדת DJ מקצועית",
            "category": "ציוד הגברה",
            "total_amount": 3,
            "amount": 3,
            "price": 250.0,
            "notes": "עמדת DJ עם כל הציוד הנדרש",
            "description": "עמדת DJ מקצועית עם מערכת שמע, תאורה ומיקסר",
            "condition": "מעולה",
            "hidden": False,
            "image": "dj_station.jpg"
        },
        {
            "name": "מכונת עשן קל",
            "category": "ציוד תאורה",
            "total_amount": 5,
            "amount": 5,
            "price": 100.0,
            "notes": "אפקט עשן קל לריקודים",
            "description": "מכונת עשן קל ליצירת אפקטים מיוחדים בריקוד הראשון",
            "condition": "מעולה",
            "hidden": False,
            "image": "smoke_machine.jpg"
        },
        {
            "name": "עמדת צילום פולארויד",
            "category": "ציוד עזר לאירועים",
            "total_amount": 2,
            "amount": 2,
            "price": 180.0,
            "notes": "עמדה לצילומים מהנים",
            "description": "עמדת צילום עם מצלמת פולארויד ואביזרי צילום כיפיים",
            "condition": "מעולה",
            "hidden": False,
            "image": "photo_booth.jpg"
        },
        {
            "name": "עגלת קוקטיילים ניידת",
            "category": "ציוד בישול וחימום",
            "total_amount": 4,
            "amount": 4,
            "price": 150.0,
            "notes": "עגלה אלגנטית למשקאות",
            "description": "עגלת קוקטיילים ניידת מעוצבת, מושלמת להגשת משקאות",
            "condition": "מעולה",
            "hidden": False,
            "image": "cocktail_cart.jpg"
        },
        {
            "name": "כיסוי כיסאות אלגנטי",
            "category": "כיסאות ושולחנות",
            "total_amount": 100,
            "amount": 100,
            "price": 15.0,
            "notes": "כיסויים לבנים לכיסאות",
            "description": "כיסוי כיסאות אלגנטי בצבע לבן עם סרט זהב",
            "condition": "מעולה",
            "hidden": False,
            "image": "chair_covers.jpg"
        },
        {
            "name": "מפות שולחן תחרה",
            "category": "אבזרי נוי ועיצוב",
            "total_amount": 35,
            "amount": 35,
            "price": 30.0,
            "notes": "מפות תחרה יפות לשולחנות",
            "description": "מפות שולחן מתחרה עדינה בצבע שמנת, מעניקות מגע רומנטי",
            "condition": "מעולה",
            "hidden": False,
            "image": "lace_tablecloth.jpg"
        }
    ]
    
    try:
        for item_data in sample_items:
            # Check if item already exists
            existing = Item.find_one({"name": item_data["name"]})
            if existing:
                print(f"Item '{item_data['name']}' already exists")
                continue
                
            item = Item(**item_data)
            item.save()
            print(f"Created item: {item_data['name']}")
            
    except Exception as e:
        print(f"Error creating sample items: {str(e)}")


def migrate_data():
    """Main migration function"""
    print("Starting MongoDB migration...")
    
    try:
        # Create Flask app context
        app = create_app_context()
        
        with app.app_context():
            # Initialize MongoDB collections and indexes
            print("Initializing database...")
            init_db()
            
            # Create users
            print("Creating users...")
            create_admin_user()
            create_sample_user()
            
            # Create sample items
            print("Creating sample items...")
            create_sample_items()
            
            print("Migration completed successfully!")
        
    except Exception as e:
        print(f"Migration failed: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    migrate_data()
