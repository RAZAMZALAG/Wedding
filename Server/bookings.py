import uuid
from bson import ObjectId
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, current_user, get_jwt
from models import Item, Order, User, Cart
from extensions import mongo
from datetime import datetime, date, timedelta
from email_utils import send_booking_pending_email, send_booking_approved_email, send_return_reminder_email, send_return_thank_you_email, send_booking_rejected_email
from logger_config import get_logger, log_database_operation, log_user_action, log_business_event, PerformanceMonitor

booking_bp = Blueprint("booking", __name__)
logger = get_logger(__name__)

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
    permission = int(claims.get("permission", 0))
    
    logger.info(f"Get bookings request from user with permission {permission}")

    if permission > 1:
        logger.debug("Admin user accessing all bookings")
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
                            "amount": cart_item.get('amount', cart_item.get('quantity', 1))  # Handle both 'amount' and 'quantity' keys
                        })

                order_dict = order.to_dict()
                order_dict.update({
                    "user": {
                        "_id": str(user._id),  # Convert ObjectId to string for JSON serialization
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
                "meta": {
                    "total_bookings": total_count,
                    "total_pages": (total_count + per_page - 1) // per_page,
                    "current_page": page,
                    "per_page": per_page
                }
            }), 200

        except Exception as e:
            logger.error("Error getting admin bookings", exc_info=True)
            return jsonify({"error": f"Error getting bookings: {str(e)}"}), 500
    else:
        # Regular user - get their own bookings
        logger.debug(f"Regular user with permission {permission} accessing own bookings")
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


@booking_bp.get('/my-bookings')
@jwt_required()
def get_my_personal_bookings():
    """Get current user's personal bookings - new endpoint"""
    try:
        logger.debug(f"My bookings request for user {current_user._id}")
        
        # Get pagination parameters
        page = int(request.args.get("page", default=1))
        per_page = int(request.args.get("per_page", default=20))
        direction = request.args.get("direction", default="desc")
        
        # Get user's orders
        orders = list(Order.get_user_orders(current_user._id))
        logger.debug(f"Found {len(orders)} orders")
        
        if not orders:
            return jsonify({
                "bookings": [],
                "total": 0,
                "page": page,
                "per_page": per_page,
                "total_pages": 0
            }), 200
        
        # Sort orders by ObjectId which contains creation timestamp
        if direction == "desc":
            # Sort using MongoDB aggregation to avoid datetime comparison issues
            orders = sorted(orders, key=lambda x: str(x._id), reverse=True)  # Convert ObjectId to string for consistent ordering
        else:
            orders = sorted(orders, key=lambda x: str(x._id))
        
        # Pagination
        total_orders = len(orders)
        start_index = (page - 1) * per_page
        end_index = start_index + per_page
        paginated_orders = orders[start_index:end_index]
        
        # Build response with cart items
        orders_data = []
        for order in paginated_orders:
            try:
                cart = Cart.find_by_id(order.cart_id)
                cart_items = []
                if cart and hasattr(cart, 'items') and cart.items:
                    logger.debug(f"Processing cart with {len(cart.items)} items for order {order._id}")
                    for cart_item in cart.items:
                        logger.debug(f"Processing cart_item: {cart_item}")
                        item = Item.find_by_id(cart_item['item_id'])
                        if item:
                            item_dict = {
                                "item": item.to_dict(),
                                "amount": cart_item.get('amount', cart_item.get('quantity', 1))  # Handle both 'amount' and 'quantity' keys
                            }
                            logger.debug(f"Added item {item.name} to order")
                            cart_items.append(item_dict)
                        else:
                            logger.warning(f"Item not found for ID: {cart_item['item_id']} in order {order._id}")
                else:
                    logger.warning(f"Cart issues for order {order._id} - cart exists: {cart is not None}, has items: {hasattr(cart, 'items') if cart else False}")
                
                order_dict = order.to_dict()
                order_dict["cart_items"] = cart_items
                orders_data.append(order_dict)
            except Exception as e:
                logger.error(f"Error processing order {order._id}", exc_info=True)
                continue
        
        return jsonify({
            "bookings": orders_data,
            "total": total_orders,
            "page": page,
            "per_page": per_page,
            "total_pages": (total_orders + per_page - 1) // per_page
        }), 200
        
    except Exception as e:
        logger.error("Error getting personal bookings", exc_info=True)
        return jsonify({"error": f"Error getting personal bookings: {str(e)}"}), 500



@booking_bp.get('/<booking_id>')
@jwt_required()
def get_booking_by_id(booking_id):
    """Get specific booking by ID"""
    # Handle special case for personal bookings
    if booking_id == "personal":
        logger.debug(f"Handling personal bookings request for user {current_user._id}")
        # Get pagination parameters
        page = int(request.args.get("page", default=1))
        per_page = int(request.args.get("per_page", default=20))
        direction = request.args.get("direction", default="desc")
        
        try:
            # Get user's orders
            orders = list(Order.get_user_orders(current_user._id))
            logger.debug(f"Found {len(orders)} orders for user {current_user._id}")
            
            if not orders:
                # No orders found - return empty result
                logger.info(f"No orders found for user {current_user._id}")
                return jsonify({
                    "bookings": [],
                    "total": 0,
                    "page": page,
                    "per_page": per_page,
                    "total_pages": 0
                }), 200
            
            # Sort orders by created_at
            if direction == "desc":
                orders.sort(key=lambda x: x.created_at, reverse=True)
            else:
                orders.sort(key=lambda x: x.created_at)
            
            # Pagination
            total_orders = len(orders)
            start_index = (page - 1) * per_page
            end_index = start_index + per_page
            paginated_orders = orders[start_index:end_index]
            
            # Build response with cart items
            orders_data = []
            for order in paginated_orders:
                cart = Cart.find_by_id(order.cart_id)
                cart_items = []
                if cart and cart.items:
                    for cart_item in cart.items:
                        item = Item.find_by_id(cart_item['item_id'])
                        if item:
                            cart_items.append({
                                "item": item.to_dict(),
                                "amount": cart_item.get('amount', cart_item.get('quantity', 1))  # Handle both 'amount' and 'quantity' keys
                            })
                
                order_dict = order.to_dict()
                order_dict["cart_items"] = cart_items
                orders_data.append(order_dict)
            
            return jsonify({
                "bookings": orders_data,
                "total": total_orders,
                "page": page,
                "per_page": per_page,
                "total_pages": (total_orders + per_page - 1) // per_page
            }), 200
            
        except Exception as e:
            return jsonify({"error": f"Error getting personal bookings: {str(e)}"}), 500
    
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
            
            if cart_item.get('amount', cart_item.get('quantity', 1)) > available_amount:
                return jsonify({
                    "error": "INSUFFICIENT_AVAILABILITY",
                    "item_name": item.name,
                    "requested": cart_item.get('amount', cart_item.get('quantity', 1)),
                    "available": available_amount
                }), 400

        # Calculate total price
        total_price = 0
        rental_days = count_booking_units(start_date, end_date)
        
        for cart_item in user_cart.items:
            item = Item.find_by_id(cart_item['item_id'])
            if item:
                total_price += item.price * cart_item.get('amount', cart_item.get('quantity', 1)) * rental_days

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
            logger.error("Error sending booking confirmation email", extra={
                "order_id": str(new_order._id),
                "user_email": current_user.email
            }, exc_info=True)

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
        logger.error("Error calculating available amount for item", extra={
            "item_id": item_id
        }, exc_info=True)
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

        valid_statuses = ["PENDING", "APPROVED", "REJECTED", "COLLECTED", "RETURNED", "COMPLETED", "CANCELLED"]
        if status.upper() not in valid_statuses:
            return jsonify({"error": "INVALID_STATUS"}), 400

        old_status = booking.status
        booking.status = status.upper()
        
        if booking.status in ["APPROVED", "COLLECTED", "RETURNED", "COMPLETED"]:
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
                    elif booking.status in ["RETURNED", "COMPLETED"]:
                        send_return_thank_you_email(
                            user.email,
                            user.first_name
                        )
                    # Note: COLLECTED status doesn't need an email notification
                    # as the customer already picked up the items
                except Exception as e:
                    logger.error("Error sending status update email", extra={
                        "booking_id": booking_id,
                        "new_status": booking.status,
                        "user_email": user.email
                    }, exc_info=True)

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


@booking_bp.put('/cart/<item_id>/increase')
@jwt_required()
def increase_cart_item_quantity(item_id):
    """Increase quantity of item in user's cart"""
    try:
        cart = Cart.get_user_cart(current_user._id)
        
        # Find the item in cart
        item_found = False
        for cart_item in cart.items:
            if cart_item['item_id'] == item_id:
                # Check if we can increase (don't exceed item's total amount)
                item = Item.find_by_id(item_id)
                if item and cart_item['amount'] < item.total_amount:
                    cart_item['amount'] += 1
                    item_found = True
                    logger.info(f"Increased quantity of item {item_id} in cart for user {current_user._id}")
                    break
                else:
                    return jsonify({"error": "CANNOT_INCREASE_QUANTITY_EXCEEDS_AVAILABLE"}), 400
        
        if not item_found:
            return jsonify({"error": "ITEM_NOT_FOUND_IN_CART"}), 404
            
        cart.save()
        return jsonify({"message": "QUANTITY_INCREASED"}), 200

    except Exception as e:
        logger.error(f"Error increasing cart item quantity: {str(e)}", exc_info=True)
        return jsonify({"error": f"Error increasing quantity: {str(e)}"}), 500


@booking_bp.put('/cart/<item_id>/decrease')
@jwt_required()
def decrease_cart_item_quantity(item_id):
    """Decrease quantity of item in user's cart"""
    try:
        cart = Cart.get_user_cart(current_user._id)
        
        # Find the item in cart
        item_found = False
        for cart_item in cart.items:
            if cart_item['item_id'] == item_id:
                if cart_item['amount'] > 1:
                    cart_item['amount'] -= 1
                    item_found = True
                    logger.info(f"Decreased quantity of item {item_id} in cart for user {current_user._id}")
                    break
                else:
                    # If quantity would become 0, remove the item instead
                    cart.items.remove(cart_item)
                    item_found = True
                    logger.info(f"Removed item {item_id} from cart for user {current_user._id} (quantity reached 0)")
                    break
        
        if not item_found:
            return jsonify({"error": "ITEM_NOT_FOUND_IN_CART"}), 404
            
        cart.save()
        return jsonify({"message": "QUANTITY_DECREASED"}), 200

    except Exception as e:
        logger.error(f"Error decreasing cart item quantity: {str(e)}", exc_info=True)
        return jsonify({"error": f"Error decreasing quantity: {str(e)}"}), 500


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
        
        # Get bookings ending in 1 day that need return reminders
        ending_orders = list(Order.get_collection().find({
            "status": {"$in": ["APPROVED", "COLLECTED"]},  # Both approved and already collected orders
            "end_date": tomorrow.isoformat()
        }))

        for order_data in ending_orders:
                order = Order(**order_data)
                cart = Cart.find_by_id(order.cart_id)
                if cart:
                    user = User.find_by_id(cart.user_id)
                    if user:
                        try:
                            # Get item names for this order
                            item_names = []
                            for item in cart.items:
                                item_obj = Item.find_by_id(item.get('item_id'))
                                if item_obj:
                                    item_names.append(item_obj.name)
                            
                            send_return_reminder_email(
                                user.email,
                                user.first_name,
                                order.end_date,
                                item_names
                            )
                        except Exception as e:
                            logger.error("Error sending return reminder email", extra={
                                "user_email": user.email,
                                "order_id": str(order._id),
                                "end_date": str(order.end_date)
                            }, exc_info=True)

        logger.info("Return reminders processing completed", extra={
            "date": str(tomorrow),
            "orders_processed": len(ending_orders)
        })

    except Exception as e:
        logger.error("Error in send_booking_return_reminders function", exc_info=True)
