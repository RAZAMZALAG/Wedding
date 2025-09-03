#!/usr/bin/env python3
"""
Test script for testing reminder emails
"""
import sys
import os
from datetime import datetime, timedelta, date

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models import Order, Cart, User, Item
from extensions import mongo
from bookings import send_booking_return_reminders
from flask import Flask

# Create a minimal Flask app for context
app = Flask(__name__)
app.config['MONGO_URI'] = 'mongodb://localhost:27017/wedding_planner'
mongo.init_app(app)

def test_reminder_system():
    """Test the reminder system manually"""
    with app.app_context():
        print("🔍 Testing reminder system...")
        
        # Get tomorrow's date
        tomorrow = (datetime.now() + timedelta(days=1)).date()
        print(f"Looking for orders ending on: {tomorrow}")
        
        # Check current orders
        all_orders = list(Order.get_collection().find({}))
        print(f"\n📋 Found {len(all_orders)} total orders in system")
        
        # Look for orders ending tomorrow
        ending_orders = list(Order.get_collection().find({
            "status": {"$in": ["APPROVED", "COLLECTED"]},
            "end_date": tomorrow.isoformat()
        }))
        
        print(f"📅 Orders ending tomorrow ({tomorrow}): {len(ending_orders)}")
        
        if ending_orders:
            for order_data in ending_orders:
                order = Order(**order_data)
                cart = Cart.find_by_id(order.cart_id)
                if cart:
                    user = User.find_by_id(cart.user_id)
                    if user:
                        print(f"  - Order {order._id} for user {user.first_name} ({user.email})")
                        
                        # Get item names
                        item_names = []
                        for item in cart.items:
                            item_obj = Item.find_by_id(item.get('item_id'))
                            if item_obj:
                                item_names.append(item_obj.name)
                        print(f"    Items: {', '.join(item_names)}")
        
        # Test sending reminders
        print("\n📧 Testing reminder sending...")
        try:
            send_booking_return_reminders()
            print("✅ Reminder function completed successfully")
        except Exception as e:
            print(f"❌ Error in reminder function: {e}")

def create_test_order():
    """Create a test order ending tomorrow for testing"""
    with app.app_context():
        tomorrow = (datetime.now() + timedelta(days=1)).date()
        print(f"🔧 Creating test order ending on {tomorrow}...")
        
        # Find an existing user and item
        user = User.get_collection().find_one({})
        item = Item.get_collection().find_one({})
        
        if not user or not item:
            print("❌ Need existing user and item in database")
            return
            
        print(f"Using user: {user['first_name']} ({user['email']})")
        print(f"Using item: {item['name']}")
        
        # Create a test cart
        from bson import ObjectId
        cart_id = ObjectId()
        
        # Handle user_id - it might be a string or ObjectId
        user_id = user['_id']
        if isinstance(user_id, str):
            # If it's a string, keep it as string
            cart_user_id = user_id
        else:
            # If it's already ObjectId, use it
            cart_user_id = ObjectId(user_id)
            
        cart_data = {
            "_id": cart_id,
            "user_id": cart_user_id,
            "items": [{
                "item_id": item['_id'],  # Keep as string if it's UUID
                "quantity": 1
            }]
        }
        
        Cart.get_collection().insert_one(cart_data)
        
        # Create test order
        order_data = {
            "_id": ObjectId(),
            "cart_id": cart_id,
            "start_date": (datetime.now().date()).isoformat(),
            "end_date": tomorrow.isoformat(),
            "status": "APPROVED",
            "total_price": 100,
            "submission_date": datetime.now(),
            "finalization_date": datetime.now()  # Changed to datetime, not date
        }
        
        Order.get_collection().insert_one(order_data)
        print(f"✅ Created test order: {order_data['_id']}")
        return order_data['_id']

if __name__ == "__main__":
    print("🧪 Reminder System Test Tool")
    print("=" * 40)
    
    if len(sys.argv) > 1 and sys.argv[1] == "--create-test":
        test_order_id = create_test_order()
        print(f"\n🎯 Test order created: {test_order_id}")
    
    test_reminder_system()
