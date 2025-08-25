import os
from flask import Blueprint, request, jsonify
from flask_jwt_extended import current_user, jwt_required
from extensions import db
from models import Item, Category, Cart, CartItem, Order
from schemas import ItemSchema, CategorySchema
from sqlalchemy import or_, and_, func
from datetime import date, datetime, timedelta
from collections import defaultdict

item_bp = Blueprint("items", __name__)


@item_bp.get('/')
@jwt_required(optional=True)
def get_paged_items():
    """Get paginated items for wedding catalog with availability checking"""
    
    # Request parameters
    page = request.args.get('page', type=int, default=1)
    amount_per_page = request.args.get('amount_per_page', type=int, default=20)
    filter_by_name = request.args.get('filter_by_name', default='')
    category = request.args.get('category', default='')
    only_available = request.args.get('only_available', type=bool, default=False)
    load_categories = request.args.get('load_categories', type=bool, default=False)

    try:
        # Base query for items
        query = db.session.query(Item)

        # Filter by name if provided
        if filter_by_name:
            query = query.filter(Item.name.ilike(f'%{filter_by_name}%'))

        # Filter by category if provided
        if category:
            query = query.filter(Item.category == category)

        # Include hidden items only if the user has permission level 2 or above
        if current_user and current_user.permission < 2:
            query = query.filter(Item.hidden == False)

        # Filter by availability (only show items with available stock for rental system)
        if only_available:
            # Get date range from query parameters for rental availability check
            start_date = request.args.get('start_date')
            end_date = request.args.get('end_date')
            
            if start_date and end_date:
                # For rental system: check availability for specific date range
                from datetime import datetime
                try:
                    start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
                    end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
                    
                    # Get overlapping bookings for the requested date range
                    overlapping_bookings = (
                        db.session.query(
                            CartItem.item_id,
                            func.sum(CartItem.amount).label("booked")
                        )
                        .join(Order, CartItem.cart_id == Order.cart_id)
                        .filter(
                            Order.status.in_(['PENDING', 'APPROVED', 'COLLECTED']),
                            # Check for date range overlap
                            Order.start_date <= end_date,
                            Order.end_date >= start_date
                        )
                        .group_by(CartItem.item_id)
                    ).subquery()
                    
                    # Filter to only show items where total_amount > booked amount for the date range
                    query = query.outerjoin(
                        overlapping_bookings, 
                        Item.id == overlapping_bookings.c.item_id
                    ).filter(
                        or_(
                            overlapping_bookings.c.booked == None,  # No overlapping bookings
                            Item.total_amount > overlapping_bookings.c.booked  # Available stock for dates
                        )
                    )
                except ValueError:
                    # Invalid date format, fall back to general availability check
                    pass
            
            if not start_date or not end_date:
                # Fall back to general availability check (all active bookings)
                ordered_quantities = (
                    db.session.query(
                        CartItem.item_id,
                        func.sum(CartItem.amount).label("ordered")
                    )
                    .join(Order, CartItem.cart_id == Order.cart_id)
                    .filter(
                        Order.status.in_(['PENDING', 'APPROVED', 'COLLECTED'])
                    )
                    .group_by(CartItem.item_id)
                ).subquery()

                # Filter to only show items where total_amount > ordered amount
                query = query.outerjoin(
                    ordered_quantities, 
                    Item.id == ordered_quantities.c.item_id
                ).filter(
                    or_(
                        ordered_quantities.c.ordered == None,  # No orders yet
                        Item.total_amount > ordered_quantities.c.ordered  # Available stock
                    )
                )

        # Paginate the items
        items = query.paginate(page=page, per_page=amount_per_page)

        # Serialize the items
        item_schema = ItemSchema(many=True)
        result = item_schema.dump(items.items)

        # Add availability information for each item
        item_ids = [item.id for item in items.items]
        if item_ids:
            # Get date range from query parameters for detailed availability calculation
            start_date = request.args.get('start_date')
            end_date = request.args.get('end_date')
            
            # Always calculate availability based on dates if provided
            if start_date and end_date:
                # For rental system: calculate availability for specific date range
                from datetime import datetime
                try:
                    start_date_parsed = datetime.strptime(start_date, '%Y-%m-%d').date()
                    end_date_parsed = datetime.strptime(end_date, '%Y-%m-%d').date()
                    
                    # Get overlapping bookings for the requested date range
                    overlapping_bookings_result = (
                        db.session.query(
                            CartItem.item_id,
                            func.sum(CartItem.amount).label("booked")
                        )
                        .join(Order, CartItem.cart_id == Order.cart_id)
                        .filter(
                            CartItem.item_id.in_(item_ids),
                            Order.status.in_(['PENDING', 'APPROVED', 'COLLECTED']),
                            # Check for date range overlap
                            Order.start_date <= end_date_parsed,
                            Order.end_date >= start_date_parsed
                        )
                        .group_by(CartItem.item_id)
                        .all()
                    )
                    
                    booked_map = {item_id: booked for item_id, booked in overlapping_bookings_result}
                    
                    # Add availability info to each item for the specific date range
                    for item_data in result:
                        total_inventory = item_data.get("total_amount", item_data["amount"])
                        booked_quantity = booked_map.get(item_data["id"], 0)
                        available_quantity = total_inventory - booked_quantity
                        
                        item_data["available_amount"] = max(0, available_quantity)
                        item_data["booked_amount"] = booked_quantity
                        item_data["in_stock"] = available_quantity > 0
                        item_data["date_range"] = f"{start_date} to {end_date}"
                        item_data["availability_calculated_for_dates"] = True
                        
                except ValueError:
                    # Invalid date format, fall back to general calculation
                    start_date = None
                    end_date = None
            
            # If no valid date range, calculate general availability (all active bookings)
            if not start_date or not end_date:
                ordered_quantities_result = (
                    db.session.query(
                        CartItem.item_id,
                        func.sum(CartItem.amount).label("ordered")
                    )
                    .join(Order, CartItem.cart_id == Order.cart_id)
                    .filter(
                        CartItem.item_id.in_(item_ids),
                        Order.status.in_(['PENDING', 'APPROVED', 'COLLECTED'])
                    )
                    .group_by(CartItem.item_id)
                    .all()
                )
                
                ordered_map = {item_id: ordered for item_id, ordered in ordered_quantities_result}
                
                # Add general availability info to each item
                for item_data in result:
                    total_inventory = item_data.get("total_amount", item_data["amount"])
                    ordered_quantity = ordered_map.get(item_data["id"], 0)
                    available_quantity = total_inventory - ordered_quantity
                    
                    item_data["available_amount"] = max(0, available_quantity)
                    item_data["ordered_amount"] = ordered_quantity
                    item_data["in_stock"] = available_quantity > 0
                    item_data["availability_calculated_for_dates"] = False
                ordered_quantity = ordered_map.get(item_data["id"], 0)
                available_quantity = total_inventory - ordered_quantity
                
                item_data["available_amount"] = max(0, available_quantity)
                item_data["ordered_amount"] = ordered_quantity
                item_data["in_stock"] = available_quantity > 0

        # Load categories if requested
        categories_list = []
        if load_categories:
            categories = db.session.query(Category.name).all()
            category_schema = CategorySchema(many=True)
            categories_list = [cat.name for cat in categories]

        return jsonify({
            "items": result,
            "total_pages": items.pages,
            "current_page": page,
            "per_page": amount_per_page,
            "total_items": items.total,
            "categories": categories_list
        }), 200

    except Exception as e:
        print(f"Error in get_paged_items: {str(e)}")
        return jsonify({"error": "Failed to fetch items"}), 500


@item_bp.get('/available')
@jwt_required(optional=True)
def get_available_items():
    """Get items with available stock for wedding orders"""
    
    try:
        # Get all items with their availability info
        items_query = db.session.query(Item)
        
        if current_user and current_user.permission < 2:
            items_query = items_query.filter(Item.hidden == False)
            
        items = items_query.all()
        
        # Calculate availability for each item
        result = []
        for item in items:
            # Get total ordered quantity
            ordered_quantity = (
                db.session.query(func.sum(CartItem.amount))
                .join(Order, CartItem.cart_id == Order.cart_id)
                .filter(
                    CartItem.item_id == item.id,
                    Order.status.in_(['PENDING', 'APPROVED', 'COLLECTED'])
                )
                .scalar() or 0
            )
            
            available_quantity = item.total_amount - ordered_quantity
            
            if available_quantity > 0:
                item_schema = ItemSchema()
                item_data = item_schema.dump(item)
                item_data["available_amount"] = available_quantity
                item_data["ordered_amount"] = ordered_quantity
                result.append(item_data)
        
        return jsonify(result), 200
        
    except Exception as e:
        print(f"Error in get_available_items: {str(e)}")
        return jsonify({"error": "Failed to fetch available items"}), 500


@item_bp.get('/categories')
def get_categories():
    """Get all item categories"""
    try:
        categories = db.session.query(Category.name).all()
        category_names = [cat.name for cat in categories]
        return jsonify(category_names), 200
    except Exception as e:
        print(f"Error in get_categories: {str(e)}")
        return jsonify({"error": "Failed to fetch categories"}), 500


@item_bp.get('/<int:item_id>')
@jwt_required(optional=True)
def get_item_by_id(item_id):
    """Get a specific item by ID with availability info"""
    try:
        item = db.session.query(Item).get(item_id)
        if not item:
            return jsonify({"error": "Item not found"}), 404
            
        if current_user and current_user.permission < 2 and item.hidden:
            return jsonify({"error": "Item not found"}), 404
            
        # Calculate availability
        ordered_quantity = (
            db.session.query(func.sum(CartItem.amount))
            .join(Order, CartItem.cart_id == Order.cart_id)
            .filter(
                CartItem.item_id == item.id,
                Order.status.in_(['PENDING', 'APPROVED', 'COLLECTED'])
            )
            .scalar() or 0
        )
        
        available_quantity = item.total_amount - ordered_quantity
        
        item_schema = ItemSchema()
        result = item_schema.dump(item)
        result["available_amount"] = max(0, available_quantity)
        result["ordered_amount"] = ordered_quantity
        result["in_stock"] = available_quantity > 0
        
        return jsonify(result), 200
        
    except Exception as e:
        print(f"Error in get_item_by_id: {str(e)}")
        return jsonify({"error": "Failed to fetch item"}), 500


# Admin functions for managing items (add, edit, delete)
@item_bp.post('/add')
@jwt_required()
def add_item():
    """Add a new wedding item (admin only)"""
    if not current_user or current_user.permission < 2:
        return jsonify({"error": "Insufficient permissions"}), 403
        
    try:
        data = request.get_json()
        
        # Create new item
        new_item = Item(
            name=data.get('name'),
            category=data.get('category'),
            amount=data.get('amount', 1),
            total_amount=data.get('total_amount', data.get('amount', 1)),
            price=data.get('price', 0),
            notes=data.get('notes', ''),
            description=data.get('description', ''),
            condition=data.get('condition', 'NEW'),
            hidden=data.get('hidden', False)
        )
        
        db.session.add(new_item)
        db.session.commit()
        
        item_schema = ItemSchema()
        return jsonify(item_schema.dump(new_item)), 201
        
    except Exception as e:
        db.session.rollback()
        print(f"Error in add_item: {str(e)}")
        return jsonify({"error": "Failed to add item"}), 500


@item_bp.put('/<int:item_id>')
@jwt_required()
def update_item(item_id):
    """Update an existing item (admin only)"""
    if not current_user or current_user.permission < 2:
        return jsonify({"error": "Insufficient permissions"}), 403
        
    try:
        item = db.session.query(Item).get(item_id)
        if not item:
            return jsonify({"error": "Item not found"}), 404
            
        data = request.get_json()
        
        # Update item fields
        if 'name' in data:
            item.name = data['name']
        if 'category' in data:
            item.category = data['category']
        if 'amount' in data:
            item.amount = data['amount']
        if 'total_amount' in data:
            item.total_amount = data['total_amount']
        if 'price' in data:
            item.price = data['price']
        if 'notes' in data:
            item.notes = data['notes']
        if 'description' in data:
            item.description = data['description']
        if 'condition' in data:
            item.condition = data['condition']
        if 'hidden' in data:
            item.hidden = data['hidden']
            
        db.session.commit()
        
        item_schema = ItemSchema()
        return jsonify(item_schema.dump(item)), 200
        
    except Exception as e:
        db.session.rollback()
        print(f"Error in update_item: {str(e)}")
        return jsonify({"error": "Failed to update item"}), 500


@item_bp.delete('/<int:item_id>')
@jwt_required()
def delete_item(item_id):
    """Delete an item (admin only)"""
    if not current_user or current_user.permission < 2:
        return jsonify({"error": "Insufficient permissions"}), 403
        
    try:
        item = db.session.query(Item).get(item_id)
        if not item:
            return jsonify({"error": "Item not found"}), 404
            
        # Check if item has any orders
        order_count = (
            db.session.query(func.count(CartItem.id))
            .join(Order, CartItem.cart_id == Order.cart_id)
            .filter(CartItem.item_id == item_id)
            .scalar()
        )
        
        if order_count > 0:
            # Don't delete items that have been ordered, just hide them
            item.hidden = True
            db.session.commit()
            return jsonify({"message": "Item hidden (has existing orders)"}), 200
        else:
            # Safe to delete
            db.session.delete(item)
            db.session.commit()
            return jsonify({"message": "Item deleted successfully"}), 200
            
    except Exception as e:
        db.session.rollback()
        print(f"Error in delete_item: {str(e)}")
        return jsonify({"error": "Failed to delete item"}), 500
