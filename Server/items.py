import os
from flask import Blueprint, request, jsonify
from flask_jwt_extended import current_user, jwt_required, get_jwt
from extensions import mongo
from models import Item, Category, Cart, Order
from datetime import date, datetime, timedelta
from collections import defaultdict
import base64

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
        # Build filter query
        filter_query = {}

        # Filter by name if provided
        if filter_by_name:
            filter_query['name'] = {'$regex': filter_by_name, '$options': 'i'}

        # Filter by category if provided
        if category:
            filter_query['category'] = category

        # Include hidden items only if the user has permission level 2 or above
        if not current_user or current_user.permission < 2:
            filter_query['hidden'] = {'$ne': True}

        # Filter by availability (only show items with available stock for rental system)
        if only_available:
            # Get date range from query parameters for rental availability check
            start_date = request.args.get('start_date')
            end_date = request.args.get('end_date')
            
            if start_date and end_date:
                # For rental system: check availability for specific date range
                try:
                    start_date = datetime.fromisoformat(start_date).date()
                    end_date = datetime.fromisoformat(end_date).date()
                    
                    # Get all items first, then filter by availability
                    all_items = list(Item.get_collection().find(filter_query))
                    available_items = []
                    
                    for item_data in all_items:
                        item = Item(**item_data)
                        if is_item_available_for_dates(item._id, start_date, end_date, item.total_amount):
                            available_items.append(item_data)
                    
                    # Manual pagination for available items
                    total_count = len(available_items)
                    start_idx = (page - 1) * amount_per_page
                    end_idx = start_idx + amount_per_page
                    items_page = available_items[start_idx:end_idx]
                    
                except ValueError as e:
                    return jsonify({"error": f"Invalid date format: {str(e)}"}), 400
            else:
                filter_query['amount'] = {'$gt': 0}  # Only items with stock
                items_cursor = Item.get_collection().find(filter_query)
                total_count = Item.get_collection().count_documents(filter_query)
                items_page = list(items_cursor.skip((page - 1) * amount_per_page).limit(amount_per_page))
        else:
            # Regular pagination without availability check
            items_cursor = Item.get_collection().find(filter_query)
            total_count = Item.get_collection().count_documents(filter_query)
            items_page = list(items_cursor.skip((page - 1) * amount_per_page).limit(amount_per_page))

        # Convert to Item objects and prepare response
        items_data = []
        for item_data in items_page:
            item = Item(**item_data)
            item_dict = item.to_dict()  # Use the to_dict method that includes 'id'
            items_data.append(item_dict)

        response_data = {
            "items": items_data,
            "total": total_count,
            "pages": (total_count + amount_per_page - 1) // amount_per_page,
            "current_page": page,
            "per_page": amount_per_page
        }

        # Include categories if requested
        if load_categories:
            categories = Category.find_all()
            response_data["categories"] = [cat.name for cat in categories]

        return jsonify(response_data), 200

    except Exception as e:
        return jsonify({"error": f"Error retrieving items: {str(e)}"}), 500


def is_item_available_for_dates(item_id, start_date, end_date, total_amount):
    """Check if item is available for the given date range"""
    try:
        # Get all orders for this item in the date range
        orders = Order.get_collection().find({
            "status": {"$nin": ["CANCELLED", "COMPLETED"]},
            "$or": [
                {
                    "start_date": {"$lte": end_date.isoformat()},
                    "end_date": {"$gte": start_date.isoformat()}
                }
            ]
        })

        # Calculate total booked amount for this item
        booked_amount = 0
        for order in orders:
            # Get cart items for this order
            cart = Cart.find_by_id(order.get("cart_id"))
            if cart and hasattr(cart, 'items'):
                for cart_item in cart.items:
                    if cart_item.get('item_id') == item_id:
                        booked_amount += cart_item.get('amount', 0)

        return (total_amount - booked_amount) > 0

    except Exception as e:
        print(f"Error checking availability for item {item_id}: {str(e)}")
        return True  # Default to available if there's an error


@item_bp.get('/available')
@jwt_required()
def get_available_items():
    """Get items available for rental in a specific date range"""
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    if not start_date or not end_date:
        return jsonify({"error": "START_DATE_AND_END_DATE_REQUIRED"}), 400

    try:
        start_date = datetime.fromisoformat(start_date).date()
        end_date = datetime.fromisoformat(end_date).date()
        
        # Get all non-hidden items
        all_items = Item.find_all({"hidden": {"$ne": True}})
        available_items = []
        
        for item in all_items:
            available_amount = get_available_amount_for_dates(item._id, start_date, end_date, item.total_amount)
            if available_amount > 0:
                item_dict = item.to_dict()
                item_dict["available_amount"] = available_amount
                available_items.append(item_dict)
        
        return jsonify({"available_items": available_items}), 200
        
    except ValueError as e:
        return jsonify({"error": f"Invalid date format: {str(e)}"}), 400
    except Exception as e:
        return jsonify({"error": f"Error getting available items: {str(e)}"}), 500


def get_available_amount_for_dates(item_id, start_date, end_date, total_amount):
    """Get available amount for item in date range"""
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


@item_bp.get('/categories')
def get_categories():
    """Get all categories"""
    try:
        categories = Category.find_all()
        return jsonify([cat.name for cat in categories]), 200
    except Exception as e:
        return jsonify({"error": f"Error getting categories: {str(e)}"}), 500


@item_bp.get('/<item_id>')
@jwt_required(optional=True)
def get_item_by_id(item_id):
    """Get single item by ID with availability info"""
    try:
        item = Item.find_by_id(item_id)
        if not item:
            return jsonify({"error": "ITEM_NOT_FOUND"}), 404

        # Check if item is hidden and user doesn't have permission
        if item.hidden and (not current_user or current_user.permission < 2):
            return jsonify({"error": "ITEM_NOT_FOUND"}), 404

        item_data = item.to_dict()
        
        # Add availability info if dates provided
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        if start_date and end_date:
            try:
                start_date = datetime.fromisoformat(start_date).date()
                end_date = datetime.fromisoformat(end_date).date()
                item_data["available_amount"] = get_available_amount_for_dates(
                    item._id, start_date, end_date, item.total_amount
                )
            except ValueError:
                pass  # Ignore invalid date formats
        
        return jsonify(item_data), 200
        
    except Exception as e:
        return jsonify({"error": f"Error getting item: {str(e)}"}), 500


@item_bp.post('/add')
@jwt_required()
def add_item():
    """Add new item (admin only)"""
    claims = get_jwt()
    if claims.get("permission", 0) < 2:
        return jsonify({"error": "FORBIDDEN"}), 403

    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['name', 'category', 'total_amount', 'price', 'description', 'condition']
        for field in required_fields:
            if not data.get(field):
                return jsonify({"error": f"MISSING_FIELD: {field}"}), 400

        # Check if category exists
        category = Category.get_by_name(data['category'])
        if not category:
            # Create new category
            new_category = Category(name=data['category'])
            new_category.save()

        # Create new item
        new_item = Item(
            name=data['name'],
            category=data['category'],
            amount=data.get('amount', data['total_amount']),
            total_amount=data['total_amount'],
            price=float(data['price']),
            notes=data.get('notes', ''),
            description=data['description'],
            condition=data['condition'],
            hidden=data.get('hidden', False),
            image=data.get('image', 'default.jpg')
        )
        
        new_item.save()
        return jsonify({"message": "ITEM_CREATED", "item_id": new_item._id}), 201
        
    except Exception as e:
        return jsonify({"error": f"Error creating item: {str(e)}"}), 500


@item_bp.put('/<item_id>')
@jwt_required()
def update_item(item_id):
    """Update item (admin only)"""
    claims = get_jwt()
    if claims.get("permission", 0) < 2:
        return jsonify({"error": "FORBIDDEN"}), 403

    try:
        item = Item.find_by_id(item_id)
        if not item:
            return jsonify({"error": "ITEM_NOT_FOUND"}), 404

        data = request.get_json()
        
        # Update fields if provided
        updateable_fields = ['name', 'category', 'amount', 'total_amount', 'price', 
                           'notes', 'description', 'condition', 'hidden', 'image']
        
        for field in updateable_fields:
            if field in data:
                if field == 'price':
                    setattr(item, field, float(data[field]))
                else:
                    setattr(item, field, data[field])

        # Check if new category exists
        if 'category' in data:
            category = Category.get_by_name(data['category'])
            if not category:
                new_category = Category(name=data['category'])
                new_category.save()

        item.save()
        return jsonify({"message": "ITEM_UPDATED"}), 200
        
    except Exception as e:
        return jsonify({"error": f"Error updating item: {str(e)}"}), 500


@item_bp.delete('/<item_id>')
@jwt_required()
def delete_item(item_id):
    """Delete item (admin only)"""
    claims = get_jwt()
    if claims.get("permission", 0) < 2:
        return jsonify({"error": "FORBIDDEN"}), 403

    try:
        item = Item.find_by_id(item_id)
        if not item:
            return jsonify({"error": "ITEM_NOT_FOUND"}), 404

        # Check if item is in any active orders
        active_orders = Order.get_collection().find({
            "status": {"$nin": ["CANCELLED", "COMPLETED"]}
        })
        
        for order in active_orders:
            cart = Cart.find_by_id(order.get("cart_id"))
            if cart and hasattr(cart, 'items'):
                for cart_item in cart.items:
                    if cart_item.get('item_id') == item_id:
                        return jsonify({"error": "ITEM_IN_ACTIVE_ORDERS"}), 400

        # Delete item
        item.delete()
        return jsonify({"message": "ITEM_DELETED"}), 200
        
    except Exception as e:
        return jsonify({"error": f"Error deleting item: {str(e)}"}), 500
