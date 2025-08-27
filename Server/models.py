from extensions import mongo
from datetime import datetime, date
from werkzeug.security import generate_password_hash, check_password_hash
from uuid import uuid4
import json


class BaseModel:
    """Base class for MongoDB models"""
    
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
        if not hasattr(self, '_id'):
            self._id = str(uuid4())
        if not hasattr(self, 'created_at'):
            self.created_at = datetime.now()
        if not hasattr(self, 'updated_at'):
            self.updated_at = datetime.now()
    
    @property
    def collection(self):
        """Get MongoDB collection for this model"""
        if hasattr(self, '_collection_name'):
            return mongo.db[self._collection_name]
        return None

    @classmethod
    def get_collection(cls):
        """Get collection for this model class"""
        instance = cls()
        if hasattr(instance, '_collection_name'):
            return mongo.db[instance._collection_name]
        return None
    
    def save(self):
        """Save or update document in MongoDB"""
        self.updated_at = datetime.now()
        document = self.to_dict()
        
        collection = self.collection
        if collection is not None and collection.find_one({'_id': document['_id']}):
            # Update existing document
            collection.update_one(
                {'_id': document['_id']}, 
                {'$set': document}
            )
        else:
            # Insert new document
            if collection is not None:
                collection.insert_one(document)
        return self
    
    def delete(self):
        """Delete document from MongoDB"""
        return self.collection.delete_one({'_id': self._id})
    
    def to_dict(self):
        """Convert model to dictionary"""
        result = {}
        for key, value in self.__dict__.items():
            if isinstance(value, date):
                result[key] = value.isoformat()
            elif isinstance(value, datetime):
                result[key] = value.isoformat()
            else:
                result[key] = value
        
        # Convert _id to id for frontend compatibility
        if '_id' in result:
            result['id'] = result['_id']
            # Keep _id for MongoDB operations
            
        return result
    
    @classmethod
    def find_by_id(cls, id):
        """Find document by ID"""
        collection = cls.get_collection()
        if collection is not None:
            document = collection.find_one({'_id': id})
            if document:
                return cls(**document)
        return None
    
    @classmethod
    def find_all(cls, filter=None):
        """Find all documents matching filter"""
        filter = filter or {}
        collection = cls.get_collection()
        if collection is not None:
            documents = collection.find(filter)
            return [cls(**doc) for doc in documents]
        return []
    
    @classmethod
    def find_one(cls, filter):
        """Find one document matching filter"""
        collection = cls.get_collection()
        if collection is not None:
            document = collection.find_one(filter)
            if document:
                return cls(**document)
        return None


class User(BaseModel):
    """User model for MongoDB"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._collection_name = 'users'
        
        # Set default values
        if not hasattr(self, 'permission'):
            self.permission = 1
        if not hasattr(self, 'blocked'):
            self.blocked = False
        if not hasattr(self, 'verified'):
            self.verified = False
    
    def make_password(self, password):
        """Hash password"""
        self.password = generate_password_hash(password)
    
    def check_password(self, password):
        """Check password against hash"""
        return check_password_hash(self.password, password)
    
    @classmethod
    def get_user_by_email(cls, email):
        """Get user by email"""
        return cls.find_one({'email': email})
    
    def __repr__(self):
        return f"<User {self.email}>"


class Category(BaseModel):
    """Category model for MongoDB"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._collection_name = 'categories'
    
    @classmethod
    def get_by_name(cls, name):
        """Get category by name"""
        return cls.find_one({'name': name})
    
    def __repr__(self):
        return f"<Category {self.name}>"


class Item(BaseModel):
    """Item model for MongoDB"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._collection_name = 'items'
        
        # Set default values
        if not hasattr(self, 'category'):
            self.category = 'כללי'
        if not hasattr(self, 'hidden'):
            self.hidden = False
    
    @classmethod
    def get_by_category(cls, category):
        """Get items by category"""
        return cls.find_all({'category': category, 'hidden': {'$ne': True}})
    
    @classmethod
    def search_items(cls, query):
        """Search items by name or description"""
        filter = {
            '$or': [
                {'name': {'$regex': query, '$options': 'i'}},
                {'description': {'$regex': query, '$options': 'i'}}
            ],
            'hidden': {'$ne': True}
        }
        return cls.find_all(filter)
    
    def __repr__(self):
        return f"<Item {self.name}>"


class Cart(BaseModel):
    """Cart model for MongoDB"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._collection_name = 'carts'
        
        # Set default values
        if not hasattr(self, 'status'):
            self.status = 'ACTIVE'
        if not hasattr(self, 'items'):
            self.items = []
    
    def add_item(self, item_id, amount=1):
        """Add item to cart"""
        # Check if item already in cart
        for cart_item in self.items:
            if cart_item['item_id'] == item_id:
                cart_item['amount'] += amount
                break
        else:
            # Add new item to cart
            self.items.append({
                'item_id': item_id,
                'amount': amount
            })
        return self.save()
    
    def remove_item(self, item_id):
        """Remove item from cart"""
        self.items = [item for item in self.items if item['item_id'] != item_id]
        return self.save()
    
    def update_item_amount(self, item_id, amount):
        """Update item amount in cart"""
        for cart_item in self.items:
            if cart_item['item_id'] == item_id:
                cart_item['amount'] = amount
                break
        return self.save()
    
    @classmethod
    def get_user_cart(cls, user_id):
        """Get active cart for user"""
        cart = cls.find_one({'user_id': user_id, 'status': 'ACTIVE'})
        if not cart:
            # Create new cart for user
            cart = cls(user_id=user_id)
            cart.save()
        return cart
    
    def __repr__(self):
        return f"<Cart id={self._id} user_id={self.user_id} status={self.status}>"


class Order(BaseModel):
    """Order model for MongoDB"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._collection_name = 'orders'
        
        # Convert string dates to date objects if needed
        if hasattr(self, 'start_date') and isinstance(self.start_date, str):
            self.start_date = datetime.fromisoformat(self.start_date).date()
        if hasattr(self, 'end_date') and isinstance(self.end_date, str):
            self.end_date = datetime.fromisoformat(self.end_date).date()
        if hasattr(self, 'submission_date') and isinstance(self.submission_date, str):
            self.submission_date = datetime.fromisoformat(self.submission_date).date()
        if hasattr(self, 'finalization_date') and isinstance(self.finalization_date, str):
            self.finalization_date = datetime.fromisoformat(self.finalization_date).date()
    
    @classmethod
    def get_user_orders(cls, user_id):
        """Get all orders for user"""
        # Get carts for user first
        user_carts = Cart.get_collection().find({'user_id': user_id})
        cart_ids = [cart['_id'] for cart in user_carts]
        
        return cls.find_all({'cart_id': {'$in': cart_ids}})
    
    @classmethod
    def get_orders_by_status(cls, status):
        """Get orders by status"""
        return cls.find_all({'status': status})
    
    @classmethod
    def get_orders_in_date_range(cls, start_date, end_date):
        """Get orders in date range"""
        if isinstance(start_date, str):
            start_date = datetime.fromisoformat(start_date).date()
        if isinstance(end_date, str):
            end_date = datetime.fromisoformat(end_date).date()
            
        return cls.find_all({
            '$or': [
                {
                    'start_date': {
                        '$gte': start_date.isoformat(),
                        '$lte': end_date.isoformat()
                    }
                },
                {
                    'end_date': {
                        '$gte': start_date.isoformat(),
                        '$lte': end_date.isoformat()
                    }
                }
            ]
        })
    
    def to_dict(self):
        """Convert to dict with proper date handling"""
        result = super().to_dict()
        
        # Convert dates to ISO format
        date_fields = ['start_date', 'end_date', 'submission_date', 'finalization_date']
        for field in date_fields:
            if hasattr(self, field) and getattr(self, field):
                value = getattr(self, field)
                if isinstance(value, date):
                    result[field] = value.isoformat()
        
        return result
    
    def __repr__(self):
        return f"<Order cart_id={self.cart_id} status={self.status}>"


# Keep Booking alias for backward compatibility
Booking = Order


def init_db():
    """Initialize database with default data"""
    try:
        # Create indexes for better performance
        mongo.db.users.create_index("email", unique=True)
        mongo.db.categories.create_index("name", unique=True)
        mongo.db.items.create_index("name")
        mongo.db.items.create_index("category")
        mongo.db.carts.create_index([("user_id", 1), ("status", 1)])
        mongo.db.orders.create_index("cart_id")
        mongo.db.orders.create_index("status")
        mongo.db.orders.create_index([("start_date", 1), ("end_date", 1)])
        
        # Insert default categories if they don't exist
        default_categories = [
            'כלי הגשה וחרסינה',
            'כיסאות ושולחנות', 
            'אבזרי נוי ועיצוב',
            'ציוד הגברה',
            'ציוד תאורה',
            'ציוד בישול וחימום',
            'ציוד עזר לאירועים',
            'הזמנות ומזכרות',
            'תכשיטים ואביזרים',
            'רכב וקישוט',
            'כללי'
        ]
        
        for category_name in default_categories:
            if not mongo.db.categories.find_one({'name': category_name}):
                category = Category(name=category_name)
                category.save()
        
        from logger_config import get_logger
        logger = get_logger(__name__)
        logger.info("Database initialized successfully with MongoDB")
        
    except Exception as e:
        from logger_config import get_logger
        logger = get_logger(__name__)
        logger.error("Error initializing database", exc_info=True)
