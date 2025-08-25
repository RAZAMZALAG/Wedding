from extensions import db
from uuid import uuid4
from werkzeug.security import generate_password_hash, check_password_hash


class User(db.Model):
    __tablename__ = "User"

    id = db.Column(db.String(256), primary_key=True, default=str(uuid4()))
    email = db.Column(db.String(120), nullable=False)
    permission = db.Column(db.Integer, nullable=False, default=1)
    password = db.Column(db.String(256), nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    phone_number = db.Column(db.String(15), nullable=False)
    location = db.Column(db.String(50), nullable=False)
    agreement = db.Column(db.Boolean, nullable=False)
    blocked = db.Column(db.Boolean, nullable=False, default=False)
    id_file = db.Column(db.LargeBinary, nullable=False)
    verified = db.Column(db.Boolean, nullable=False, default=False) 

    def make_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def save(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.commit()

    @classmethod
    def get_user_by_email(cls, email):
        return cls.query.filter_by(email=email).first()

    def __repr__(self):
        return f"<User {self.email}>"


class Item(db.Model):
    __tablename__ = "Item"

    id = db.Column(db.String(256), primary_key=True, default=str(uuid4()))
    name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(100), db.ForeignKey("Category.name", ondelete='SET DEFAULT'), nullable=False, default='כללי')
    amount = db.Column(db.Integer, nullable=False)
    total_amount = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)
    notes = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(256), nullable=False)
    condition = db.Column(db.String(100), nullable=False)
    hidden = db.Column(db.Boolean, nullable=False)
    image = db.Column(db.String(64), nullable=False)

    def save(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.commit()

    def __repr__(self):
        return f"<Item {self.id}>"


class Category(db.Model):
    __tablename__ = "Category"

    name = db.Column(db.String(100), primary_key=True)

    def save(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.commit()

    def __repr__(self):
        return f"<Category {self.name}>"


class Cart(db.Model):
    __tablename__ = 'Cart'

    id = db.Column(db.String(256), primary_key=True)
    user_id = db.Column(db.String(256), db.ForeignKey('User.id', ondelete='CASCADE'), nullable=False)
    status = db.Column(db.String(20), nullable=False, default='ACTIVE')

    # Relationship to get the items in the cart via CartItem
    items = db.relationship('CartItem', back_populates='cart', cascade='all, delete-orphan')

    def __repr__(self):
        return f"<Cart id={self.id} user_id={self.user_id} status={self.status}>"


class CartItem(db.Model):
    __tablename__ = 'CartItem'

    cart_id = db.Column(db.String(256), db.ForeignKey('Cart.id', ondelete='CASCADE'), nullable=False, primary_key=True)
    item_id = db.Column(db.String(256), db.ForeignKey('Item.id', ondelete='CASCADE'), nullable=False, primary_key=True)
    amount = db.Column(db.Integer, nullable=False, default=1)

    # Relationship to Cart and Item
    cart = db.relationship('Cart', back_populates='items')
    item = db.relationship('Item', backref='cart_items')

    def __repr__(self):
        return f"<CartItem cart_id={self.cart_id} item_id={self.item_id} amount={self.amount}>"


class Order(db.Model):
    __tablename__ = 'Order'

    cart_id = db.Column(db.String(256), db.ForeignKey('Cart.id'), primary_key=True)
    cart = db.relationship('Cart', backref='orders')
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    submission_date = db.Column(db.Date, nullable=False)
    finalization_date = db.Column(db.Date, nullable=True)
    total_price = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(20), nullable=False)
    customer_notes = db.Column(db.String(500), nullable=True)

    # Table arguments: Check constraints and Primary key constraint
    __table_args__ = (
        db.CheckConstraint('total_price > 0', name='check_total_price_positive'),
    )

    def save(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

# Keep Booking class for backward compatibility for now
Booking = Order
