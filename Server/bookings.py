import uuid

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, current_user, get_jwt
from models import Item, Order, User, Cart, CartItem
from schemas import BookingSchema, CartSchema, ItemSchema
from extensions import db
from datetime import datetime, date
from sqlalchemy import case, func
from email_utils import send_booking_pending_email, send_booking_approved_email, send_return_reminder_email, send_return_thank_you_email, send_booking_rejected_email
from datetime import datetime, timedelta

booking_bp = Blueprint("booking", __name__)

# For backward compatibility, we'll alias Order as Booking
Booking = Order


# For rental system, we calculate rental duration in days
def count_booking_units(start_date, end_date):
    # Calculate the number of days in the rental period
    if isinstance(start_date, str):
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
    if isinstance(end_date, str):
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
    
    # Calculate the rental duration in days
    duration = (end_date - start_date).days + 1  # +1 to include both start and end days
    return max(1, duration)  # Minimum 1 day


@booking_bp.get('/')
@jwt_required()
def get_bookings():
    claims = get_jwt()

    # Check if the user has the required permission level
    if int(claims.get("permission")) > 1:
        # Get query parameters with default values
        page = request.args.get("page", default=1, type=int)
        per_page = request.args.get("per_page", default=20, type=int)
        booking_type = request.args.get("type", default="all")
        order_by = request.args.get("order_by", default="start_date")  # Default sort by start_date
        direction = request.args.get("direction", default="asc")  # Default to ascending order
        filter_by_name = request.args.get("filter_by_name", "")
        filter_by_email = request.args.get("filter_by_email", "")

        query = Order.query.join(Cart, Order.cart_id == Cart.id)

        # Only join User ONCE, and only if needed
        if filter_by_name or filter_by_email or order_by == "user_name":
            query = query.join(User, Cart.user_id == User.id)

        # Apply status filter if provided
        if booking_type != "all":
            if booking_type == "SCHEDULED":
                # SCHEDULED: PENDING or APPROVED orders
                query = query.filter((Order.status.in_(["PENDING", "APPROVED"])))
            elif booking_type == "EXISTING":
                # EXISTING: Orders that are being processed or collected
                query = query.filter(Order.status == "COLLECTED")
            elif booking_type == "DONE":
                # DONE: Completed or rejected orders
                query = query.filter(Order.status.in_(["REJECTED", "RETURNED"]))

        # Get today's date for reference
        today = date.today()

        # Check if the user wants to order by 'late' orders (for wedding planning context)
        if order_by == "late":
            # For wedding orders, "late" might mean orders past their end date
            query = query.order_by(
                case(
                    (Order.status == 'COLLECTED', Order.end_date < today),  # Past end date
                    else_=False
                ).desc(),
                Order.start_date.asc() if direction == "asc" else Order.start_date.desc()
            )
        else:
            # Apply sorting for other fields (item_name, user_name, start_date, end_date)
            if order_by == "item_name":
                query = query.join(Item).order_by(
                    getattr(Item, "name").asc() if direction == "asc" else getattr(Item, "name").desc())
            elif order_by == "user_name":
                if direction == "asc":
                    query = query.order_by(User.first_name.asc(), User.last_name.asc())
                else:
                    query = query.order_by(User.first_name.desc(), User.last_name.desc())
            elif order_by == "start_date":
                query = query.order_by(
                    Order.start_date.asc() if direction == "asc" else Order.start_date.desc())
            elif order_by == "end_date":
                query = query.order_by(
                    Order.end_date.asc() if direction == "asc" else Order.end_date.desc())
            else:
                # Default to sorting by start_date
                query = query.order_by(
                    Order.start_date.asc() if direction == "asc" else Order.start_date.desc()
                )
        
        if filter_by_name:
            query = query.filter(
                (User.first_name.ilike(f"%{filter_by_name}%")) |
                (User.last_name.ilike(f"%{filter_by_name}%"))
            )
            
        if filter_by_email:
            query = query.filter(User.email.ilike(f"%{filter_by_email}%"))

        # Paginate the query results
        bookings = query.paginate(page=page, per_page=per_page, error_out=False)

        # Now, get the items for each booking
        bookings_with_items = []
        for booking in bookings.items:
            # Fetch the associated items for the current booking
            cart_items = CartItem.query.filter_by(cart_id=booking.cart_id).join(Item).all()
            items = []
            for cart_item in cart_items:
                items.append({
                    "id": cart_item.item_id,
                    "name": cart_item.item.name,
                    "amount": cart_item.amount,
                    "price": cart_item.item.price,
                })

            cart = Cart.query.filter_by(id=booking.cart_id).first()
            user = User.query.filter_by(id=cart.user_id).first()

            # Add items info to each booking
            booking_info = BookingSchema().dump(booking)
            booking_info["items"] = items
            booking_info["user"] = {
                "first_name": user.first_name,
                "last_name": user.last_name,
                "email": user.email
            }
            bookings_with_items.append(booking_info)

        # Return the paginated result with items and metadata
        return jsonify({
            "bookings": bookings_with_items,
            "meta": {
                "total_bookings": bookings.total,
                "total_pages": bookings.pages,
                "current_page": bookings.page,
                "per_page": per_page
            }
        }), 200
    else:
        return jsonify({"error": "UNAUTHORIZED"}), 401


@booking_bp.get('/cart')
@jwt_required()
def get_current_cart():
    user_id = current_user.id  # Get the current logged-in user's ID

    # Query to find the cart with the 'ACTIVE' status for the current user
    active_cart = Cart.query.filter_by(user_id=user_id, status='ACTIVE').first()

    # If no active cart exists, return a 404 error
    if not active_cart:
        # If no active cart exists, create a new cart
        active_cart = Cart(
            id=str(uuid.uuid4()),  # Generate a unique cart ID
            user_id=user_id,
            status='ACTIVE'
        )
        db.session.add(active_cart)
        db.session.commit()

    # Serialize the cart using the CartSchema
    cart_schema = CartSchema()
    cart_data = cart_schema.dump(active_cart)

    # Now, we also need to include the items in the cart, so we'll query the CartItem model
    cart_items = CartItem.query.filter_by(cart_id=active_cart.id).all()

    # Get all the item details in the cart
    items_data = []
    for cart_item in cart_items:
        item = Item.query.get(cart_item.item_id)
        item_data = ItemSchema().dump(item)
        item_data['amount'] = cart_item.amount  # Include the quantity of the item in the cart
        items_data.append(item_data)

    # Add the items to the cart response
    cart_data['items'] = items_data

    return jsonify(cart_data), 200


@booking_bp.post('/cart/add/<item_id>')
@jwt_required()
def add_item_to_cart(item_id):
    # Fetch the item from the database
    item = Item.query.get(item_id)
    if not item:
        return jsonify({'error': 'ITEM_NOT_FOUND'}), 404

    # Fetch the user's active cart or create one if it doesn't exist
    user_id = current_user.id
    active_cart = Cart.query.filter_by(user_id=user_id, status='ACTIVE').first()

    if not active_cart:
        # If no active cart exists, create a new cart
        active_cart = Cart(
            id=str(uuid.uuid4()),  # Generate a unique cart ID
            user_id=user_id,
            status='ACTIVE'
        )
        db.session.add(active_cart)
        db.session.commit()

    # Check if the item is already in the cart
    cart_item = CartItem.query.filter_by(cart_id=active_cart.id, item_id=item_id).first()

    if cart_item:
        # If the item already exists in the cart, update the quantity
        cart_item.amount += 1  # Default amount is 1
        db.session.commit()
        return jsonify({'message': 'ITEM_QUANTITY_UPDATED'}), 200
    else:
        # If the item is not in the cart, add it with default amount 1
        new_cart_item = CartItem(
            cart_id=active_cart.id,
            item_id=item_id,
            amount=1  # Default amount is 1
        )
        db.session.add(new_cart_item)
        db.session.commit()

        return jsonify({'message': 'ITEM_ADDED_TO_CART'}), 201


@booking_bp.delete('/cart/remove/<item_id>')
@jwt_required()
def remove_item_from_cart(item_id):
    # Fetch the user's active cart
    user_id = current_user.id
    active_cart = Cart.query.filter_by(user_id=user_id, status='ACTIVE').first()

    if not active_cart:
        return jsonify({'error': 'ACTIVE_CART_NOT_FOUND'}), 404

    # Check if the item exists in the cart
    cart_item = CartItem.query.filter_by(cart_id=active_cart.id, item_id=item_id).first()

    if not cart_item:
        return jsonify({'error': 'ITEM_NOT_IN_CART'}), 404

    # Remove the item from the cart
    db.session.delete(cart_item)
    db.session.commit()

    return jsonify({'message': 'ITEM_REMOVED_FROM_CART'}), 200


@booking_bp.put('/cart/<string:item_id>/increase')
@jwt_required()
def increase_item_amount(item_id):
    # Fetch the active cart for the current user
    cart = Cart.query.filter_by(user_id=current_user.id, status='ACTIVE').first()
    if not cart:
        return jsonify({'error': 'ACTIVE_CART_NOT_FOUND'}), 404

    # Fetch the cart item using cart_id and item_id
    cart_item = CartItem.query.filter_by(cart_id=cart.id, item_id=item_id).first()
    if not cart_item:
        return jsonify({'error': 'ITEM_NOT_IN_CART'}), 404

    # Fetch the item details from the Item table using item_id
    item = Item.query.get(item_id)
    if not item:
        return jsonify({'error': 'ITEM_NOT_FOUND'}), 404

    # Check if the amount can be increased (maximum = total_amount of the item)
    if cart_item.amount < item.total_amount:
        cart_item.amount += 1
        db.session.commit()
        return jsonify({'message': f'Amount for item {item.name} increased by 1.'}), 200
    else:
        return jsonify({'error': 'MAX_AMOUNT_REACHED'}), 400


@booking_bp.put('/cart/<string:item_id>/decrease')
@jwt_required()
def decrease_item_amount(item_id):
    # Fetch the active cart for the current user
    cart = Cart.query.filter_by(user_id=current_user.id, status='ACTIVE').first()
    if not cart:
        return jsonify({'error': 'ACTIVE_CART_NOT_FOUND'}), 404

    # Fetch the cart item using cart_id and item_id
    cart_item = CartItem.query.filter_by(cart_id=cart.id, item_id=item_id).first()
    if not cart_item:
        return jsonify({'error': 'ITEM_NOT_IN_CART'}), 404

    # Fetch the item details from the Item table using item_id
    item = Item.query.get(item_id)
    if not item:
        return jsonify({'error': 'ITEM_NOT_FOUND'}), 404

    # Check if the amount can be decreased (minimum = 1)
    if cart_item.amount > 1:
        cart_item.amount -= 1
        db.session.commit()
        return jsonify({'message': f'Amount for item {item.name} decreased by 1.'}), 200
    else:
        return jsonify({'error': 'MIN_AMOUNT_REACHED'}), 400


@booking_bp.get('/personal')
@jwt_required()
def get_personal_bookings():
    user_id = current_user.id
    page = request.args.get("page", default=1, type=int)
    amount_per_page = request.args.get("amount_per_page", default=20, type=int)
    filter_by_name = request.args.get("filter_by_name", default="", type=str)
    status = request.args.get("status", default="", type=str)

    # Fetch bookings related to the user
    query = Booking.query.join(Cart).filter(Cart.user_id == user_id)

    if status:
        query = query.filter(Booking.status == status)

    if filter_by_name:
        # Join CartItem and Item to filter by item name
        query = query.join(CartItem).join(Item).filter(Item.name.ilike(f"%{filter_by_name}%"))

    # Paginate the bookings
    bookings = query.paginate(page=page, per_page=amount_per_page, count=True)

    # Now, get the items for each booking
    bookings_with_items = []
    for booking in bookings.items:
        # Fetch the associated items for the current booking
        cart_items = CartItem.query.filter_by(cart_id=booking.cart_id).join(Item).all()
        items = []
        for cart_item in cart_items:
            items.append({
                "id": cart_item.item_id,
                "name": cart_item.item.name,
                "amount": cart_item.amount,
                "price": cart_item.item.price,
            })

        # Add items info to each booking
        booking_info = BookingSchema().dump(booking)
        booking_info["items"] = items
        bookings_with_items.append(booking_info)

    # Create the response
    metadata = {
        "page": page,
        "total_pages": bookings.pages,
        "total_bookings": bookings.total,
        "bookings_per_page": amount_per_page,
    }

    res = {
        "bookings": bookings_with_items,
        "meta": metadata
    }

    return jsonify(res), 200


@booking_bp.post('/book')
@jwt_required()
def book():
    data = request.get_json()

    # Validate required fields for wedding order
    required_fields = ['start_date', 'end_date']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': 'MISSING_FIELDS'}), 400

    # Convert start and end dates to datetime objects
    try:
        start_date = datetime.strptime(data['start_date'], '%Y-%m-%d')
        end_date = datetime.strptime(data['end_date'], '%Y-%m-%d')
    except ValueError:
        return jsonify({'error': 'INVALID_DATE_FORMAT'}), 400

    # Validate that end_date is not before start_date
    if end_date < start_date:
        return jsonify({'error': 'END_DATE_BEFORE_START_DATE'}), 400

    # Fetch or create active cart for the user
    cart = Cart.query.filter_by(user_id=current_user.id, status='ACTIVE').first()
    if not cart:
        return jsonify({'error': 'CART_NOT_FOUND'}), 400

    # For wedding orders, unit count is always 1 per item
    unit_count = 1

    # Calculate the total price based on the cart items
    total_price = 0
    for cart_item in cart.items:
        item = cart_item.item  # Accessing the item through CartItem
        total_price += item.price * cart_item.amount

    # Check inventory availability for each item based on date range
    for cart_item in cart.items:
        item = cart_item.item
        total_available = item.total_amount if hasattr(item, "total_amount") else item.amount

        # For rental orders, check if enough items are available for the requested date range
        overlapping_orders = (
            db.session.query(func.sum(CartItem.amount))
            .join(Cart, CartItem.cart_id == Cart.id)
            .join(Order, Order.cart_id == Cart.id)
            .filter(
                CartItem.item_id == item.id,
                Order.status.in_(['PENDING', 'APPROVED', 'COLLECTED']),
                # Check for date range overlap
                Order.start_date <= end_date.date(),
                Order.end_date >= start_date.date()
            )
            .scalar()
        )
        overlapping_orders = overlapping_orders or 0

        # If not enough available for this date range, reject
        if overlapping_orders + cart_item.amount > total_available:
            return jsonify({'error': f'NOT_ENOUGH_{item.name}_AVAILABLE_FOR_DATES'}), 400

    # Get customer notes if provided
    customer_notes = data.get('customer_notes', '')

    # Calculate rental duration in days
    rental_days = (end_date - start_date).days + 1
    
    # Recalculate total price based on rental duration
    total_price = 0
    for cart_item in cart.items:
        item = cart_item.item
        total_price += item.price * cart_item.amount * rental_days

    # Create a new order record
    order = Order(
        cart_id=cart.id,
        start_date=start_date.date(),
        end_date=end_date.date(),
        submission_date=datetime.now().date(),
        total_price=total_price,
        status='PENDING',
        customer_notes=customer_notes
    )

    # Update the cart status to 'BOOKED'
    cart.status = 'BOOKED'
    db.session.add(cart)
    db.session.add(order)
    db.session.commit()
    
    # Send confirmation email
    item_names = [cart_item.item.name for cart_item in cart.items]
    send_booking_pending_email(
        to_email=current_user.email,
        name=current_user.first_name,
        items=item_names,
        start_date=start_date.date(),
        end_date=end_date.date()
    )

    return jsonify({'message': 'ORDER_SUCCESSFUL'}), 201


def set_booking_status(status):
    # Check permissions
    claims = get_jwt()
    if int(claims.get("permission")) < 2:
        return jsonify({"error": "UNAUTHORIZED"}), 401

    data = request.get_json()

    # Validate required fields
    required_fields = ['cart_id']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': 'MISSING FIELDS'}), 400

    booking = Booking.query.filter_by(cart_id=data['cart_id']).first()
    if not booking:
        return jsonify({"error": "BOOKING_NOT_FOUND"}), 404

    # Handle the finalization_date
    if status in ['RETURNED', 'REJECTED']:
        booking.finalization_date = datetime.now()
        # Restore item amounts if booking is being rejected/returned and was not collected
        if booking.status != 'COLLECTED':
            for cart_item in booking.cart.items:
                item = cart_item.item
                item.amount += cart_item.amount
                db.session.add(item)

    # Restore item amounts if moving from COLLECTED to another status
    if status != 'COLLECTED' and booking.status == 'COLLECTED':
        for cart_item in booking.cart.items:
            item = cart_item.item
            item.amount += cart_item.amount
            db.session.add(item)

    # DECREASE item amounts if moving from REJECTED/RETURNED to APPROVED or COLLECTED
    if status in ['APPROVED', 'COLLECTED'] and booking.status in ['REJECTED', 'RETURNED']:
        for cart_item in booking.cart.items:
            item = cart_item.item
            if item.amount < cart_item.amount:
                return jsonify({'error': f'NOT_ENOUGH_{item.name}_IN_STOCK'}), 400
            item.amount -= cart_item.amount
            db.session.add(item)

    # DECREASE item amounts if moving from not COLLECTED to COLLECTED (original logic)
    elif status == 'COLLECTED' and booking.status != 'COLLECTED':
        for cart_item in booking.cart.items:
            item = cart_item.item
            if item.amount < cart_item.amount:
                return jsonify({'error': f'NOT_ENOUGH_{item.name}_IN_STOCK'}), 400
            item.amount -= cart_item.amount
            db.session.add(item)

    booking.status = status
    db.session.add(booking)
    # send aprroval email if status is APPROVED
    if status == 'APPROVED':
        user = User.query.get(booking.cart.user_id)
        items = [cart_item.item.name for cart_item in booking.cart.items]
        send_booking_approved_email(
            user.email,
            user.first_name,
            items,
            booking.total_price,
            booking.start_date,
            booking.end_date
        )

    # Send thank-you email if status is RETURNED
    if status == 'RETURNED':
        user = User.query.get(booking.cart.user_id)
        items = [cart_item.item.name for cart_item in booking.cart.items]
        send_return_thank_you_email(
            to_email=user.email,
            name=user.first_name,
        )

    # Send rejection email if status is REJECTED
    if status == 'REJECTED':
        user = User.query.get(booking.cart.user_id)
        items = [cart_item.item.name for cart_item in booking.cart.items]
        send_booking_rejected_email(
            to_email=user.email,
            name=user.first_name,
            items=items
        )



    db.session.commit()

    return jsonify({"message": "BOOKING_STATUS_SET"}), 200


@booking_bp.put('/pending')
@jwt_required()
def pending_booking():
    return set_booking_status('PENDING')


@booking_bp.put('/approve')
@jwt_required()
def approve_booking():
    return set_booking_status('APPROVED')


@booking_bp.put('/reject')
@jwt_required()
def reject_booking():
    return set_booking_status('REJECTED')


@booking_bp.put('/collect')
@jwt_required()
def collect_booking():
    return set_booking_status('COLLECTED')


@booking_bp.put('/return')
@jwt_required()
def return_booking():
    return set_booking_status('RETURNED')


@booking_bp.patch('/start_date/<string:booking_id>')
@jwt_required()
def edit_start_date(booking_id):
    claims = get_jwt()
    permission = int(claims.get("permission"))

    if permission <= 1:
        return jsonify({"error": "UNAUTHORIZED"}), 401

    # Fetch the booking
    booking = Booking.query.get(booking_id)
    if not booking:
        return jsonify({"error": "BOOKING_NOT_FOUND"}), 404

    # Validate the input date
    data = request.get_json()
    new_start_date_str = data.get("start_date")
    if not new_start_date_str:
        return jsonify({"error": "MISSING_START_DATE"}), 400

    try:
        new_start_date = datetime.strptime(new_start_date_str, '%Y-%m-%d').date()
    except ValueError:
        return jsonify({"error": "INVALID_DATE_FORMAT"}), 400

    # Compare the new start date with the current end date
    if new_start_date >= booking.end_date:
        return jsonify({"error": "START_DATE_BEFORE_END_DATE"}), 400

    # Update the booking's start date
    booking.start_date = datetime.combine(new_start_date, datetime.min.time()).date()

    unit_count = count_booking_units(booking.start_date, booking.end_date)

    # Recalculate the total price based on the cart items and new unit count
    total_price = 0
    for cart_item in booking.cart.items:
        item = cart_item.item  # Accessing the item through CartItem
        total_price += item.price * cart_item.amount * unit_count

    # Update the total price in the booking
    booking.total_price = total_price

    db.session.commit()

    return jsonify({"message": "START_DATE_UPDATED", "total_price": total_price}), 200


@booking_bp.patch('/end_date/<string:booking_id>')
@jwt_required()
def edit_end_date(booking_id):
    claims = get_jwt()
    permission = int(claims.get("permission"))

    if permission <= 1:
        return jsonify({"error": "UNAUTHORIZED"}), 401

    # Fetch the booking
    booking = Booking.query.get(booking_id)
    if not booking:
        return jsonify({"error": "BOOKING_NOT_FOUND"}), 404

    # Validate the input date
    data = request.get_json()
    new_end_date_str = data.get("end_date")
    if not new_end_date_str:
        return jsonify({"error": "MISSING_END_DATE"}), 400

    try:
        new_end_date = datetime.strptime(new_end_date_str, '%Y-%m-%d').date()
    except ValueError:
        return jsonify({"error": "INVALID_DATE_FORMAT"}), 400

    # Compare the new end date with the current start date
    if new_end_date <= booking.start_date:
        return jsonify({"error": "END_DATE_BEFORE_START_DATE"}), 400

    # Update the booking's end date
    booking.end_date = datetime.combine(new_end_date, datetime.min.time()).date()

    unit_count = count_booking_units(booking.start_date, booking.end_date)

    # Recalculate the total price based on the cart items and new unit count
    total_price = 0
    for cart_item in booking.cart.items:
        item = cart_item.item  # Accessing the item through CartItem
        total_price += item.price * cart_item.amount * unit_count

    # Update the total price in the booking
    booking.total_price = total_price

    db.session.commit()

    return jsonify({"message": "END_DATE_UPDATED", "total_price": total_price}), 200


@booking_bp.get('/item_bookings')
@jwt_required()
def get_bookings_for_items():
    # Get item IDs from query params: ?item_ids=id1,id2,id3
    item_ids = request.args.get('item_ids', '')
    if not item_ids:
        return jsonify({'error': 'NO_ITEM_IDS'}), 400
    item_ids = item_ids.split(',')

    # Find all bookings for these items with relevant statuses
    bookings = (
        db.session.query(Booking, CartItem)
        .join(Cart, Booking.cart_id == Cart.id)
        .join(CartItem, CartItem.cart_id == Cart.id)
        .filter(
            CartItem.item_id.in_(item_ids),
            Booking.status.in_(["PENDING", "APPROVED", "COLLECTED"])
        )
        .all()
    )

    # Group bookings by item_id
    result = {}
    for booking, cart_item in bookings:
        item_id = cart_item.item_id
        if item_id not in result:
            result[item_id] = []
        result[item_id].append({
            "start_date": booking.start_date.isoformat(),
            "end_date": booking.end_date.isoformat(),
            "status": booking.status,
            "amount": cart_item.amount,
        })

    return jsonify(result), 200

def send_booking_return_reminders():
    print("🔔 Running reminder task...")
    
    # For wedding rental system, we send return reminders one day before end date
    reminder_date = datetime.today().date() + timedelta(days=1)  # 1 day before end date

    orders = Order.query.filter(
        Order.status == 'COLLECTED',
        Order.end_date == reminder_date
    ).all()

    for order in orders:
        cart = order.cart
        user = User.query.get(cart.user_id)
        items = [f"{ci.item.name} (x{ci.amount})" for ci in cart.items]

        print(f"📩 Sending return reminder to {user.email} for items due on {order.end_date}")
        # We could send return reminders here
        # send_return_reminder_email(
        #     to_email=user.email,
        #     name=user.first_name,
        #     end_date=order.end_date,
        #     item_names=items
        # )

    print(f"🔔 Processed {len(orders)} return reminders")