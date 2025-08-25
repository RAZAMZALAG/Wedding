#!/usr/bin/env python3
"""
Script to populate the database with wedding categories and items
"""

from extensions import db
from models import Category, Item
from main import create_app

# Wedding categories (Hebrew)
WEDDING_CATEGORIES = [
    "פרחים ועיצוב",       # Flowers and Design
    "קייטרינג ומזון",      # Catering and Food
    "שמלות כלה",          # Wedding Dresses
    "חליפות חתן",         # Groom Suits
    "אבזרי נוי",          # Decorative Accessories
    "צילום ווידאו",       # Photography and Video
    "מוזיקה והופעות",     # Music and Entertainment
    "הזמנות ומזכרות",     # Invitations and Souvenirs
    "תכשיטים ואביזרים",   # Jewelry and Accessories
    "רכב וקישוט"         # Transportation and Decoration
]

def populate_wedding_data():
    """Populate the database with wedding categories and items"""
    
    app = create_app()
    
    with app.app_context():
        try:
            print("🗑️ Clearing existing categories and items...")
            
            # Clear existing data
            Item.query.delete()
            Category.query.delete()
            db.session.commit()
            
            print("📂 Adding wedding categories...")
            
            # Add wedding categories
            for category_name in WEDDING_CATEGORIES:
                category = Category(name=category_name)
                db.session.add(category)
                print(f"   ✅ Added category: {category_name}")
            
            db.session.commit()
            
            print("🎯 Adding sample wedding items...")
            
            # Add some sample wedding items
            sample_items = [
                # פרחים ועיצוב - Flowers and Design
                {"name": "זר כלה קלאסי", "category": "פרחים ועיצוב", "price": 350, "total_amount": 10},
                {"name": "עיצוב שולחן חתן כלה", "category": "פרחים ועיצוב", "price": 250, "total_amount": 5},
                {"name": "קשתות פרחים", "category": "פרחים ועיצוב", "price": 400, "total_amount": 3},
                
                # קייטרינג ומזון - Catering and Food
                {"name": "סט כלים חגיגיים", "category": "קייטרינג ומזון", "price": 150, "total_amount": 20},
                {"name": "מכונת קפה מקצועית", "category": "קייטרינג ומזון", "price": 200, "total_amount": 5},
                {"name": "מערכת הגשה", "category": "קייטרינג ומזון", "price": 300, "total_amount": 8},
                
                # שמלות כלה - Wedding Dresses
                {"name": "שמלת כלה נסיכה", "category": "שמלות כלה", "price": 2500, "total_amount": 3},
                {"name": "שמלת כלה עדינה", "category": "שמלות כלה", "price": 2000, "total_amount": 5},
                
                # חליפות חתן - Groom Suits
                {"name": "חליפת חתן שחורה", "category": "חליפות חתן", "price": 800, "total_amount": 8},
                {"name": "חליפת חתן כחולה", "category": "חליפות חתן", "price": 750, "total_amount": 6},
                
                # אבזרי נוי - Decorative Accessories
                {"name": "נרות דקורטיביים", "category": "אבזרי נוי", "price": 50, "total_amount": 50},
                {"name": "מפיות חגיגיות", "category": "אבזרי נוי", "price": 30, "total_amount": 100},
                
                # צילום ווידאו - Photography and Video
                {"name": "מצלמה מקצועית", "category": "צילום ווידאו", "price": 1500, "total_amount": 3},
                {"name": "תאורה לצילום", "category": "צילום ווידאו", "price": 400, "total_amount": 5},
                
                # מוזיקה והופעות - Music and Entertainment
                {"name": "מערכת הגברה", "category": "מוזיקה והופעות", "price": 600, "total_amount": 4},
                {"name": "מיקרופון אלחוטי", "category": "מוזיקה והופעות", "price": 100, "total_amount": 10},
                
                # הזמנות ומזכרות - Invitations and Souvenirs
                {"name": "הזמנות מעוצבות", "category": "הזמנות ומזכרות", "price": 5, "total_amount": 500},
                {"name": "מזכרות לאורחים", "category": "הזמנות ומזכרות", "price": 15, "total_amount": 200},
                
                # תכשיטים ואביזרים - Jewelry and Accessories
                {"name": "עגילי כלה", "category": "תכשיטים ואביזרים", "price": 200, "total_amount": 15},
                {"name": "שרשרת כלה", "category": "תכשיטים ואביזרים", "price": 250, "total_amount": 10},
                
                # רכב וקישוט - Transportation and Decoration
                {"name": "קישוט רכב חתונה", "category": "רכב וקישוט", "price": 150, "total_amount": 20},
                {"name": "סרטים לרכב", "category": "רכב וקישוט", "price": 50, "total_amount": 30}
            ]
            
            for i, item_data in enumerate(sample_items, 1):
                from uuid import uuid4
                item = Item(
                    id=str(uuid4()),  # Generate unique ID for each item
                    name=item_data["name"],
                    category=item_data["category"],
                    price=item_data["price"],
                    total_amount=item_data["total_amount"],
                    amount=item_data["total_amount"],  # Set amount = total_amount
                    description=f"פריט חתונה מיוחד - {item_data['name']}",
                    condition="NEW",
                    hidden=False,
                    notes="",
                    image=""
                )
                db.session.add(item)
                print(f"   🎉 Added item: {item_data['name']} (₪{item_data['price']})")
            
            db.session.commit()
            
            print("\n✅ Wedding data population completed!")
            print(f"📊 Added {len(WEDDING_CATEGORIES)} categories")
            print(f"🎁 Added {len(sample_items)} items")
            
            # Verify the data
            categories_count = Category.query.count()
            items_count = Item.query.count()
            print(f"\n🔍 Database verification:")
            print(f"   Categories in DB: {categories_count}")
            print(f"   Items in DB: {items_count}")
            
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            db.session.rollback()
            raise

if __name__ == "__main__":
    print("🚀 Starting wedding data population...")
    populate_wedding_data()
