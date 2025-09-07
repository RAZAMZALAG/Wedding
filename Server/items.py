import os
from flask import Blueprint, request, jsonify
from flask_jwt_extended import current_user, jwt_required, get_jwt
from extensions import mongo
from models import Item, Category, Cart, Order
from datetime import date, datetime, timedelta
from collections import defaultdict
from logger_config import get_logger, log_database_operation, log_user_action, PerformanceMonitor
import base64

item_bp = Blueprint("items", __name__)
logger = get_logger(__name__)


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
            filter_query['$or'] = [
                {'hidden': {'$ne': True}},
                {'hidden': {'$exists': False}}
            ]

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
        start_date_str = request.args.get('start_date')
        end_date_str = request.args.get('end_date')
        
        for item_data in items_page:
            item = Item(**item_data)
            item_dict = item.to_dict()  # Use the to_dict method that includes 'id'
            
            # If date range provided, calculate available amount for display
            if start_date_str and end_date_str:
                try:
                    start_date = datetime.fromisoformat(start_date_str).date()
                    end_date = datetime.fromisoformat(end_date_str).date()
                    
                    # Calculate available amount for the specific date range
                    available_amount = get_available_amount_for_dates(
                        item._id, start_date, end_date, item.total_amount
                    )
                    item_dict['available_amount'] = available_amount
                    
                    # Add booking information
                    booked_amount = item.total_amount - available_amount
                    item_dict['booked_amount'] = booked_amount
                    
                except ValueError:
                    # If date parsing fails, show total amount
                    item_dict['available_amount'] = item.total_amount
                    item_dict['booked_amount'] = 0
            else:
                # No date range specified, show total amount
                item_dict['available_amount'] = item.total_amount  
                item_dict['booked_amount'] = 0
                
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
                    if str(cart_item.get('item_id')) == str(item_id):
                        booked_amount += cart_item.get('amount', 0)

        return max(0, total_amount - booked_amount)
    
    except Exception as e:
        logger.error("Error calculating available amount for item", extra={
            "item_id": item_id
        }, exc_info=True)
        return total_amount


def is_item_available_for_dates(item_id, start_date, end_date, total_amount):
    """Check if item is available for the given date range"""
    try:
        available_amount = get_available_amount_for_dates(item_id, start_date, end_date, total_amount)
        return available_amount > 0
    except Exception as e:
        logger.error(f"Error checking availability for item {item_id}", exc_info=True)
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
        logger.warning("Unauthorized item creation attempt", extra={
            "user_permission": claims.get("permission", 0),
            "required_permission": 2
        })
        return jsonify({"error": "FORBIDDEN"}), 403

    try:
        # Get form data
        name = request.form.get('name')
        category = request.form.get('category')
        price = request.form.get('price')
        amount = request.form.get('amount')
        total_amount = request.form.get('total_amount')
        hidden = request.form.get('hidden', 'false').lower() == 'true'
        image_file = request.files.get('image')
        
        logger.info("Admin creating new item", extra={
            "user_id": claims.get("user_id"),
            "item_name_value": name,  # שינינו מ- item_name ל- item_name_value
            "category": category,
            "amount": amount,
            "total_amount": total_amount,
            "price": price,
            "hidden": hidden,
            "has_image": bool(image_file),
            "form_data_keys": list(request.form.keys()),
            "files_keys": list(request.files.keys())
        })
        
        # Validate required fields
        missing_fields = []
        if not name:
            missing_fields.append("name")
        if not category:
            missing_fields.append("category")
        if not price:
            missing_fields.append("price")
        if not amount:
            missing_fields.append("amount")
            
        if missing_fields:
            logger.warning("Item creation failed - missing fields", extra={
                "missing_fields": missing_fields
            })
            return jsonify({"error": f"MISSING_FIELD: {', '.join(missing_fields)}"}), 400
            
        # Validate numeric values
        try:
            amount_int = int(amount)
            total_amount_int = int(total_amount) if total_amount else amount_int
            price_float = float(price)
            if amount_int <= 0 or price_float <= 0 or total_amount_int <= 0:
                raise ValueError("Amount, total_amount and price must be positive")
        except ValueError as e:
            logger.warning("Item creation failed - invalid numeric values", extra={
                "amount": amount,
                "total_amount": total_amount,
                "price": price,
                "error": str(e)
            })
            return jsonify({"error": "Invalid amount, total_amount or price values"}), 400

        # Check if category exists
        category_obj = Category.get_by_name(category)
        if not category_obj:
            # Create new category
            logger.info("Creating new category for item", extra={"category": category})
            new_category = Category(name=category)
            new_category.save()
            logger.info("New category created successfully", extra={"category": category})

        # Handle image file
        image_filename = None
        if image_file:
            # Save image file (you might want to implement proper file handling)
            image_filename = image_file.filename
            logger.debug("Image file uploaded for item", extra={
                "filename": image_filename,
                "item_name_value": name
            })

        # Create new item
        new_item = Item(
            name=name,
            category=category,
            amount=amount_int,
            total_amount=total_amount_int,
            price=price_float,
            notes='',
            description='',
            condition='מעולה',
            hidden=hidden,
            image=image_filename or 'default.jpg'
        )
        
        new_item.save()
        
        logger.info("New item created successfully", extra={
            "item_id": str(new_item._id),
            "item_name_value": name,
            "category": category,
            "amount": amount_int,
            "price": price_float,
            "hidden": hidden,
            "created_by": claims.get("user_id")
        })
        
        # Return the created item data
        item_data = {
            "id": str(new_item._id),
            "name": new_item.name,
            "category": new_item.category,
            "amount": new_item.amount,
            "total_amount": new_item.total_amount,
            "available_amount": new_item.amount,  # Current available equals amount for new items
            "price": new_item.price,
            "notes": new_item.notes,
            "description": new_item.description,
            "condition": new_item.condition,
            "hidden": new_item.hidden,
            "image": new_item.image
        }
        
        return jsonify(item_data), 201
        
    except Exception as e:
        logger.error("Error creating new item", extra={
            "item_name_value": name if 'name' in locals() else 'unknown',
            "category": category if 'category' in locals() else 'unknown',
            "user_id": claims.get("user_id")
        }, exc_info=True)
        return jsonify({"error": f"Error creating item: {str(e)}"}), 500


@item_bp.put('/<item_id>')
@jwt_required()
def update_item(item_id):
    """Update item (admin only)"""
    claims = get_jwt()
    if claims.get("permission", 0) < 2:
        logger.warning("Unauthorized item update attempt", extra={
            "user_permission": claims.get("permission", 0),
            "item_id": item_id
        })
        return jsonify({"error": "FORBIDDEN"}), 403

    try:
        item = Item.find_by_id(item_id)
        if not item:
            logger.warning("Item update failed - item not found", extra={
                "item_id": item_id,
                "user_id": claims.get("user_id")
            })
            return jsonify({"error": "ITEM_NOT_FOUND"}), 404

        # Support both JSON and FormData
        if request.content_type and 'application/json' in request.content_type:
            data = request.get_json()
        else:
            # Handle FormData
            data = {}
            for field in request.form:
                if field == 'hidden':
                    data[field] = request.form.get(field, 'false').lower() == 'true'
                elif field in ['price', 'amount', 'total_amount']:
                    try:
                        data[field] = float(request.form.get(field))
                    except (ValueError, TypeError):
                        data[field] = request.form.get(field)
                else:
                    data[field] = request.form.get(field)
        
        logger.info("Admin updating item", extra={
            "item_id": item_id,
            "item_name": item.name,
            "user_id": claims.get("user_id"),
            "update_fields": list(data.keys()) if data else [],
            "received_data": {k: v for k, v in data.items() if k in ['amount', 'total_amount']}
        })
        
        # Track changes for logging
        changes = {}
        
        # Update fields if provided
        updateable_fields = ['name', 'category', 'amount', 'total_amount', 'price', 
                           'notes', 'description', 'condition', 'hidden', 'image']
        
        for field in updateable_fields:
            if field in data:
                old_value = getattr(item, field, None)
                new_value = data[field]
                
                if field == 'price':
                    new_value = float(new_value)
                    setattr(item, field, new_value)
                elif field == 'amount':
                    new_value = int(new_value)
                    setattr(item, field, new_value)
                    # Don't automatically update total_amount when updating amount
                    # total_amount should be updated independently if provided
                elif field == 'total_amount':
                    new_value = int(new_value)
                    setattr(item, field, new_value)
                else:
                    setattr(item, field, new_value)
                
                if old_value != new_value:
                    changes[field] = {
                        "old": old_value,
                        "new": new_value
                    }

        # Check if new category exists
        if 'category' in data:
            category = Category.get_by_name(data['category'])
            if not category:
                logger.info("Creating new category during item update", extra={
                    "category": data['category'],
                    "item_id": item_id
                })
                new_category = Category(name=data['category'])
                new_category.save()
                logger.info("New category created during item update", extra={
                    "category": data['category']
                })

        item.save()
        
        logger.info("Item updated successfully", extra={
            "item_id": item_id,
            "item_name": item.name,
            "changes": changes,
            "updated_by": claims.get("user_id")
        })
        
        # Return the updated item data
        updated_item = item.to_dict()
        # Calculate available_amount based on bookings (for now, assume no date restrictions)
        # TODO: Calculate based on actual bookings for the item
        updated_item['available_amount'] = item.amount  # Current available amount in stock
        
        logger.info("Returning updated item", extra={
            "item_id": item_id,
            "current_amount": item.amount,
            "total_amount": item.total_amount,
            "available_amount_returned": updated_item['available_amount'],
            "full_response": {k: v for k, v in updated_item.items() if k in ['amount', 'total_amount', 'available_amount']}
        })
        
        return jsonify(updated_item), 200
        
    except Exception as e:
        logger.error("Error updating item", extra={
            "item_id": item_id,
            "user_id": claims.get("user_id")
        }, exc_info=True)
        return jsonify({"error": f"Error updating item: {str(e)}"}), 500


@item_bp.delete('/<item_id>')
@jwt_required()
def delete_item(item_id):
    """Delete item (admin only)"""
    claims = get_jwt()
    if claims.get("permission", 0) < 2:
        logger.warning("Unauthorized item deletion attempt", extra={
            "user_permission": claims.get("permission", 0),
            "item_id": item_id
        })
        return jsonify({"error": "FORBIDDEN"}), 403

    try:
        item = Item.find_by_id(item_id)
        if not item:
            logger.warning("Item deletion failed - item not found", extra={
                "item_id": item_id,
                "user_id": claims.get("user_id")
            })
            return jsonify({"error": "ITEM_NOT_FOUND"}), 404

        logger.info("Admin attempting to delete item", extra={
            "item_id": item_id,
            "item_name": item.name,
            "category": item.category,
            "user_id": claims.get("user_id")
        })

        # Check if item is in any active orders
        active_orders = Order.get_collection().find({
            "status": {"$nin": ["CANCELLED", "COMPLETED"]}
        })
        
        active_order_count = 0
        for order in active_orders:
            cart = Cart.find_by_id(order.get("cart_id"))
            if cart and hasattr(cart, 'items'):
                for cart_item in cart.items:
                    if cart_item.get('item_id') == item_id:
                        active_order_count += 1
                        break
        
        if active_order_count > 0:
            logger.warning("Item deletion blocked - item is in active orders", extra={
                "item_id": item_id,
                "item_name": item.name,
                "active_orders_count": active_order_count,
                "user_id": claims.get("user_id")
            })
            return jsonify({"error": "ITEM_IN_ACTIVE_ORDERS"}), 400

        # Delete item
        item.delete()
        
        logger.info("Item deleted successfully", extra={
            "item_id": item_id,
            "item_name": item.name,
            "category": item.category,
            "deleted_by": claims.get("user_id")
        })
        
        return jsonify({"message": "ITEM_DELETED"}), 200
        
    except Exception as e:
        logger.error("Error deleting item", extra={
            "item_id": item_id,
            "user_id": claims.get("user_id")
        }, exc_info=True)
        return jsonify({"error": f"Error deleting item: {str(e)}"}), 500
