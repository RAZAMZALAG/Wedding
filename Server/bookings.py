import uuid
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, current_user, get_jwt
from models import Item, Order, User, Cart
from extensions import mongo
from datetime import datetime, date, timedelta
from email_utils import send_booking_pending_email, send_booking_approved_email, send_return_reminder_email, send_return_thank_you_email, send_booking_rejected_email

booking_bp = Blueprint("booking", __name__)

# For backward compatibility, we'll alias Order as Booking
Booking = Order


def count_booking_units(start_date, end_date):
    """Calculate the number of days in the rental period"""
    if isinstance(start_date, str):
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
    if isinstance(end_date, str):
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
    
    duration = (end_date - start_date).days + 1  # +1 to include both start and end days
    return max(1, duration)  # Minimum 1 day


@booking_bp.get('/')
@jwt_required()
def get_bookings():
    """Get bookings with filtering and pagination"""
    claims = get_jwt()

    if int(claims.get("permission", 0)) > 1:
        try:
            # Get query parameters with default values
            page = request.args.get("page", default=1, type=int)
            per_page = request.args.get("per_page", default=20, type=int)
            booking_type = request.args.get("type", default="all")
            order_by = request.args.get("order_by", default="start_date")
            direction = request.args.get("direction", default="asc")
            filter_by_name = request.args.get("filter_by_name", "")
            filter_by_email = request.args.get("filter_by_email", "")

            # Build filter query
            filter_query = {}

            # Filter by booking type/status
            if booking_type != "all":
                if booking_type == "active":
                    filter_query["status"] = {"$nin": ["CANCELLED", "COMPLETED"]}
                else:
                    filter_query["status"] = booking_type.upper()

            # Get orders
            orders_cursor = Order.get_collection().find(filter_query)
            
            # Build sort criteria
            sort_direction = 1 if direction == "asc" else -1
            if order_by == "start_date":
                orders_cursor = orders_cursor.sort("start_date", sort_direction)
            elif order_by == "submission_date":
                orders_cursor = orders_cursor.sort("submission_date", sort_direction)
            elif order_by == "total_price":
                orders_cursor = orders_cursor.sort("total_price", sort_direction)

            # Convert to list and get user info
            all_orders = list(orders_cursor)
            enriched_orders = []

            for order_data in all_orders:
                order = Order(**order_data)
                
                # Get cart and user info
                cart = Cart.find_by_id(order.cart_id)
                if not cart:
                    continue
                    
                user = User.find_by_id(cart.user_id)
                if not user:
                    continue

                # Apply name and email filters
                full_name = f"{user.first_name} {user.last_name}".lower()
                if filter_by_name and filter_by_name.lower() not in full_name:
                    continue
                if filter_by_email and filter_by_email.lower() not in user.email.lower():
                    continue

                # Get cart items with item details
                cart_items = []
                for cart_item in cart.items:
                    item = Item.find_by_id(cart_item['item_id'])
                    if item:
                        cart_items.append({
                            "item": item.to_dict(),
                            "amount": cart_item['amount']
                        })

                order_dict = order.to_dict()
                order_dict.update({
                    "user": {
                        "_id": user._id,
                        "first_name": user.first_name,
                        "last_name": user.last_name,
                        "email": user.email,
                        "phone_number": user.phone_number
                    },
                    "cart_items": cart_items
                })
                
                enriched_orders.append(order_dict)

            # Manual pagination
            total_count = len(enriched_orders)
            start_idx = (page - 1) * per_page
            end_idx = start_idx + per_page
            paginated_orders = enriched_orders[start_idx:end_idx]

            return jsonify({
                "bookings": paginated_orders,
                "total": total_count,
                "pages": (total_count + per_page - 1) // per_page,
                "current_page": page,
                "per_page": per_page
            }), 200

        except Exception as e:
            return jsonify({"error": f"Error getting bookings: {str(e)}"}), 500
    else:
        # Regular user - get their own bookings
        try:
            user_orders = Order.get_user_orders(current_user._id)
            orders_data = []
            
            for order in user_orders:
                cart = Cart.find_by_id(order.cart_id)
                if cart:
                    # Get cart items
                    cart_items = []
                    for cart_item in cart.items:
                        item = Item.find_by_id(cart_item['item_id'])
                        if item:
                            cart_items.append({
                                "item": item.to_dict(),
                                "amount": cart_item['amount']
                            })
                    
                    order_dict = order.to_dict()
                    order_dict["cart_items"] = cart_items
                    orders_data.append(order_dict)
            
            return jsonify({"bookings": orders_data}), 200
            
        except Exception as e:
            return jsonify({"error": f"Error getting user bookings: {str(e)}"}), 500


@booking_bp.get('/<booking_id>')
@jwt_required()
def get_booking_by_id(booking_id):
    """Get specific booking by ID"""
    try:
        booking = Order.find_by_id(booking_id)
        if not booking:
            return jsonify({"error": "BOOKING_NOT_FOUND"}), 404

        # Get cart and user info
        cart = Cart.find_by_id(booking.cart_id)
        if not cart:
            return jsonify({"error": "CART_NOT_FOUND"}), 404

        # Check permissions
        claims = get_jwt()
        if int(claims.get("permission", 0)) <= 1:
            # Regular user can only see their own bookings
            if cart.user_id != current_user._id:
                return jsonify({"error": "FORBIDDEN"}), 403

        user = User.find_by_id(cart.user_id)
        if not user:
            return jsonify({"error": "USER_NOT_FOUND"}), 404

        # Get cart items
        cart_items = []
        for cart_item in cart.items:
            item = Item.find_by_id(cart_item['item_id'])
            if item:
                cart_items.append({
                    "item": item.to_dict(),
                    "amount": cart_item['amount']
                })

        booking_dict = booking.to_dict()
        booking_dict.update({
            "user": {
                "_id": user._id,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "email": user.email,
                "phone_number": user.phone_number
            },
            "cart_items": cart_items
        })

        return jsonify(booking_dict), 200

    except Exception as e:
        return jsonify({"error": f"Error getting booking: {str(e)}"}), 500


@booking_bp.post('/')
@jwt_required()
def create_booking():
    """Create new booking from cart"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['start_date', 'end_date']
        for field in required_fields:
            if not data.get(field):
                return jsonify({"error": f"MISSING_FIELD: {field}"}), 400

        # Get user's active cart
        user_cart = Cart.get_user_cart(current_user._id)
        if not user_cart or not user_cart.items:
            return jsonify({"error": "EMPTY_CART"}), 400

        # Parse dates
        try:
            start_date = datetime.fromisoformat(data['start_date']).date()
            end_date = datetime.fromisoformat(data['end_date']).date()
        except ValueError:
            return jsonify({"error": "INVALID_DATE_FORMAT"}), 400

        if start_date >= end_date:
            return jsonify({"error": "INVALID_DATE_RANGE"}), 400

        # Check item availability
        for cart_item in user_cart.items:
            item = Item.find_by_id(cart_item['item_id'])
            if not item:
                return jsonify({"error": f"ITEM_NOT_FOUND: {cart_item['item_id']}"}), 404

            # Check availability for this item
            available_amount = get_available_amount_for_dates(
                item._id, start_date, end_date, item.total_amount
            )
            
            if cart_item['amount'] > available_amount:
                return jsonify({
                    "error": "INSUFFICIENT_AVAILABILITY",
                    "item_name": item.name,
                    "requested": cart_item['amount'],
                    "available": available_amount
                }), 400

        # Calculate total price
        total_price = 0
        rental_days = count_booking_units(start_date, end_date)
        
        for cart_item in user_cart.items:
            item = Item.find_by_id(cart_item['item_id'])
            if item:
                total_price += item.price * cart_item['amount'] * rental_days

        # Create order
        new_order = Order(
            cart_id=user_cart._id,
            start_date=start_date,
            end_date=end_date,
            submission_date=date.today(),
            total_price=total_price,
            status="PENDING",
            customer_notes=data.get('customer_notes', '')
        )
        
        new_order.save()

        # Update cart status to ordered
        user_cart.status = "ORDERED"
        user_cart.save()

        # Send notification email
        try:
            send_booking_pending_email(
                current_user.email,
                current_user.first_name,
                new_order._id,
                start_date,
                end_date,
                total_price
            )
        except Exception as e:
            print(f"Error sending booking email: {str(e)}")

        return jsonify({
            "message": "BOOKING_CREATED",
            "booking_id": new_order._id,
            "total_price": total_price
        }), 201

    except Exception as e:
        return jsonify({"error": f"Error creating booking: {str(e)}"}), 500


def get_available_amount_for_dates(item_id, start_date, end_date, total_amount):
    """Helper function to get available amount for item in date range"""
    try:
        # Get overlapping orders
        orders = Order.get_collection().find({
            "status": {"$nin": ["CANCELLED", "COMPLETED"]},
            "$or": [
                {
                    "start_date": {"$lte": end_date.isoformat()},
                    "end_date": {"$gte": start_date.isoformat()}
                }
            ]
        })

        booked_amount = 0
        for order in orders:
            cart = Cart.find_by_id(order.get("cart_id"))
            if cart and hasattr(cart, 'items'):
                for cart_item in cart.items:
                    if cart_item.get('item_id') == item_id:
                        booked_amount += cart_item.get('amount', 0)

        return max(0, total_amount - booked_amount)
    
    except Exception as e:
        print(f"Error calculating available amount for item {item_id}: {str(e)}")
        return total_amount


@booking_bp.put('/<booking_id>/status/<status>')
@jwt_required()
def update_booking_status(booking_id, status):
    """Update booking status (admin only)"""
    claims = get_jwt()
    if int(claims.get("permission", 0)) <= 1:
        return jsonify({"error": "FORBIDDEN"}), 403

    try:
        booking = Order.find_by_id(booking_id)
        if not booking:
            return jsonify({"error": "BOOKING_NOT_FOUND"}), 404

        valid_statuses = ["PENDING", "APPROVED", "REJECTED", "COMPLETED", "CANCELLED"]
        if status.upper() not in valid_statuses:
            return jsonify({"error": "INVALID_STATUS"}), 400

        old_status = booking.status
        booking.status = status.upper()
        
        if booking.status in ["APPROVED", "COMPLETED"]:
            booking.finalization_date = date.today()
        
        booking.save()

        # Send appropriate notification email
        cart = Cart.find_by_id(booking.cart_id)
        if cart:
            user = User.find_by_id(cart.user_id)
            if user:
                try:
                    if booking.status == "APPROVED":
                        send_booking_approved_email(
                            user.email,
                            user.first_name,
                            booking_id,
                            booking.start_date,
                            booking.end_date
                        )
                    elif booking.status == "REJECTED":
                        send_booking_rejected_email(
                            user.email,
                            user.first_name,
                            booking_id
                        )
                    elif booking.status == "COMPLETED":
                        send_return_thank_you_email(
                            user.email,
                            user.first_name,
                            booking_id
                        )
                except Exception as e:
                    print(f"Error sending status update email: {str(e)}")

        return jsonify({"message": f"BOOKING_STATUS_UPDATED_TO_{booking.status}"}), 200

    except Exception as e:
        return jsonify({"error": f"Error updating booking status: {str(e)}"}), 500


@booking_bp.get('/cart')
@jwt_required()
def get_user_cart():
    """Get current user's cart"""
    try:
        cart = Cart.get_user_cart(current_user._id)
        
        cart_items = []
        total_price = 0
        
        for cart_item in cart.items:
            item = Item.find_by_id(cart_item['item_id'])
            if item:
                item_total = item.price * cart_item['amount']
                total_price += item_total
                
                cart_items.append({
                    "item": item.to_dict(),
                    "amount": cart_item['amount'],
                    "item_total": item_total
                })

        return jsonify({
            "cart_id": cart._id,
            "items": cart_items,
            "total_price": total_price,
            "status": cart.status
        }), 200

    except Exception as e:
        return jsonify({"error": f"Error getting cart: {str(e)}"}), 500


@booking_bp.post('/cart/add')
@booking_bp.post('/cart/add/<item_id>')
@jwt_required()
def add_to_cart(item_id=None):
    """Add item to cart"""
    try:
        data = request.get_json() or {}
        
        # Get item_id from path parameter or request body
        if not item_id:
            item_id = data.get('item_id')
        
        amount = data.get('amount', 1)
        
        if not item_id:
            return jsonify({"error": "ITEM_ID_REQUIRED"}), 400
            
        # Validate amount
        if amount <= 0:
            return jsonify({"error": "INVALID_AMOUNT"}), 400

        # Check if item exists
        item = Item.find_by_id(item_id)
        if not item:
            return jsonify({"error": "ITEM_NOT_FOUND"}), 404

        # Get user's cart
        cart = Cart.get_user_cart(current_user._id)
        cart.add_item(item_id, amount)

        return jsonify({"message": "ITEM_ADDED_TO_CART"}), 200

    except Exception as e:
        return jsonify({"error": f"Error adding to cart: {str(e)}"}), 500


@booking_bp.put('/cart/update')
@jwt_required()
def update_cart_item():
    """Update item amount in cart"""
    try:
        data = request.get_json()
        
        item_id = data.get('item_id')
        amount = data.get('amount')
        
        if not item_id or amount is None:
            return jsonify({"error": "ITEM_ID_AND_AMOUNT_REQUIRED"}), 400
            
        if amount < 0:
            return jsonify({"error": "INVALID_AMOUNT"}), 400

        cart = Cart.get_user_cart(current_user._id)
        
        if amount == 0:
            cart.remove_item(item_id)
        else:
            cart.update_item_amount(item_id, amount)

        return jsonify({"message": "CART_UPDATED"}), 200

    except Exception as e:
        return jsonify({"error": f"Error updating cart: {str(e)}"}), 500


@booking_bp.delete('/cart/remove/<item_id>')
@jwt_required()
def remove_from_cart(item_id):
    """Remove item from cart"""
    try:
        if not item_id:
            return jsonify({"error": "ITEM_ID_REQUIRED"}), 400

        cart = Cart.get_user_cart(current_user._id)
        cart.remove_item(item_id)

        return jsonify({"message": "ITEM_REMOVED_FROM_CART"}), 200

    except Exception as e:
        return jsonify({"error": f"Error removing from cart: {str(e)}"}), 500


@booking_bp.delete('/cart/clear')
@jwt_required()
def clear_cart():
    """Clear user's cart"""
    try:
        cart = Cart.get_user_cart(current_user._id)
        cart.items = []
        cart.save()
        
        return jsonify({"message": "CART_CLEARED"}), 200

    except Exception as e:
        return jsonify({"error": f"Error clearing cart: {str(e)}"}), 500


def send_booking_return_reminders():
    """Send return reminders for bookings ending soon"""
    try:
        # Get bookings ending in 1 day
        tomorrow = (datetime.now() + timedelta(days=1)).date()
        
        # Get bookings ending in 1 day
        ending_orders = Order.get_collection().find({
            "status": "APPROVED",
            "end_date": tomorrow.isoformat()
        })

        for order_data in ending_orders:
                order = Order(**order_data)
                cart = Cart.find_by_id(order.cart_id)
                if cart:
                    user = User.find_by_id(cart.user_id)
                    if user:
                        try:
                            send_return_reminder_email(
                                user.email,
                                user.first_name,
                                order._id,
                                order.end_date
                            )
                        except Exception as e:
                            print(f"Error sending reminder to {user.email}: {str(e)}")

        print(f"Return reminders processed for {tomorrow}")

    except Exception as e:
        print(f"Error in send_booking_return_reminders: {str(e)}")
