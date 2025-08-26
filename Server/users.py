from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt
from models import User
from schemas import ManagedUserSchema, UserIdFileSchema
from validation import is_valid_permission
import base64

user_bp = Blueprint("users", __name__)


@user_bp.get('/')
@jwt_required()
def get_all_users():
    claims = get_jwt()
    if int(claims.get("permission", 0)) > 2:
        try:
            page = request.args.get("page", default=1, type=int)
            per_page = request.args.get("per_page", default=20, type=int)
            blocked_param = request.args.get("blocked", default="0", type=str)
            blocked = blocked_param.lower() in ["1", "true", "yes"]
            order_by = request.args.get("order_by", default=None, type=str)
            direction = request.args.get("direction", default="asc", type=str)

            # Build filter
            filter_query = {"blocked": blocked}
            
            # Build sort criteria
            sort_criteria = []
            if order_by:
                sort_direction = -1 if direction == "desc" else 1
                if order_by == "name":
                    sort_criteria = [("first_name", sort_direction), ("last_name", sort_direction)]
                elif order_by == "email":
                    sort_criteria = [("email", sort_direction)]
                elif order_by == "phone_number":
                    sort_criteria = [("phone_number", sort_direction)]
                elif order_by == "location":
                    sort_criteria = [("location", sort_direction)]

            # Get users with pagination
            users = User.get_collection().find(filter_query)
            if sort_criteria:
                users = users.sort(sort_criteria)
            
            # Manual pagination
            skip = (page - 1) * per_page
            users_list = list(users.skip(skip).limit(per_page))
            total_count = User.get_collection().count_documents(filter_query)
            
            # Convert to User objects and serialize
            user_objects = [User(**user_data) for user_data in users_list]
            result = []
            
            for user in user_objects:
                user_data = {
                    "_id": user._id,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "email": user.email,
                    "phone_number": user.phone_number,
                    "location": user.location,
                    "permission": user.permission,
                    "blocked": user.blocked,
                    "verified": user.verified,
                    "agreement": user.agreement
                }
                result.append(user_data)

            return jsonify({
                "users": result,
                "total": total_count,
                "pages": (total_count + per_page - 1) // per_page,
                "current_page": page,
                "per_page": per_page
            }), 200
            
        except Exception as e:
            return jsonify({"error": f"Error retrieving users: {str(e)}"}), 500
    else:
        return jsonify({"error": "FORBIDDEN"}), 403


@user_bp.post('/<user_id>/permission/<permission>')
@jwt_required()
def set_user_permission(user_id, permission):
    claims = get_jwt()
    if int(claims.get("permission", 0)) > 2:
        if not is_valid_permission(permission):
            return jsonify({"error": "INVALID_PERMISSION"}), 400

        try:
            user = User.find_by_id(user_id)
            if not user:
                return jsonify({"error": "USER_NOT_FOUND"}), 404

            user.permission = int(permission)
            user.save()
            
            return jsonify({"message": "USER_PERMISSION_UPDATED"}), 200
            
        except Exception as e:
            return jsonify({"error": f"Error updating permission: {str(e)}"}), 500
    else:
        return jsonify({"error": "FORBIDDEN"}), 403


@user_bp.post('/<user_id>/block')
@jwt_required()
def block_user(user_id):
    claims = get_jwt()
    if int(claims.get("permission", 0)) > 2:
        try:
            user = User.find_by_id(user_id)
            if not user:
                return jsonify({"error": "USER_NOT_FOUND"}), 404

            user.blocked = True
            user.save()
            
            return jsonify({"message": "USER_BLOCKED"}), 200
            
        except Exception as e:
            return jsonify({"error": f"Error blocking user: {str(e)}"}), 500
    else:
        return jsonify({"error": "FORBIDDEN"}), 403


@user_bp.post('/<user_id>/unblock')
@jwt_required()
def unblock_user(user_id):
    claims = get_jwt()
    if int(claims.get("permission", 0)) > 2:
        try:
            user = User.find_by_id(user_id)
            if not user:
                return jsonify({"error": "USER_NOT_FOUND"}), 404

            user.blocked = False
            user.save()
            
            return jsonify({"message": "USER_UNBLOCKED"}), 200
            
        except Exception as e:
            return jsonify({"error": f"Error unblocking user: {str(e)}"}), 500
    else:
        return jsonify({"error": "FORBIDDEN"}), 403


@user_bp.get('/<user_id>/id-file')
@jwt_required()
def get_user_id_file(user_id):
    claims = get_jwt()
    if int(claims.get("permission", 0)) > 2:
        try:
            user = User.find_by_id(user_id)
            if not user:
                return jsonify({"error": "USER_NOT_FOUND"}), 404

            if not hasattr(user, 'id_file') or not user.id_file:
                return jsonify({"error": "NO_ID_FILE"}), 404

            # Convert binary data to base64 for JSON response
            id_file_b64 = base64.b64encode(user.id_file).decode('utf-8')
            
            return jsonify({
                "id_file": id_file_b64,
                "user_name": f"{user.first_name} {user.last_name}"
            }), 200
            
        except Exception as e:
            return jsonify({"error": f"Error retrieving ID file: {str(e)}"}), 500
    else:
        return jsonify({"error": "FORBIDDEN"}), 403


@user_bp.delete('/<user_id>')
@jwt_required()
def delete_user(user_id):
    claims = get_jwt()
    if int(claims.get("permission", 0)) > 2:
        try:
            # Check if user has active orders first
            from models import Order, Cart
            
            # Find user's carts
            user_carts = Cart.find_all({"user_id": user_id})
            cart_ids = [cart._id for cart in user_carts]
            
            if cart_ids:
                # Check for active orders
                active_orders = Order.find_all({
                    "cart_id": {"$in": cart_ids},
                    "status": {"$nin": ["COMPLETED", "CANCELLED"]}
                })
                
                if active_orders:
                    return jsonify({"error": "USER_HAS_ACTIVE_ORDERS"}), 400

            # Delete user
            user = User.find_by_id(user_id)
            if not user:
                return jsonify({"error": "USER_NOT_FOUND"}), 404
                
            user.delete()
            
            # Delete user's carts and completed orders
            for cart in user_carts:
                cart.delete()
            
            # Delete completed orders for this user
            completed_orders = Order.find_all({
                "cart_id": {"$in": cart_ids},
                "status": {"$in": ["COMPLETED", "CANCELLED"]}
            })
            for order in completed_orders:
                order.delete()
            
            return jsonify({"message": "USER_DELETED"}), 200
            
        except Exception as e:
            return jsonify({"error": f"Error deleting user: {str(e)}"}), 500
    else:
        return jsonify({"error": "FORBIDDEN"}), 403


@user_bp.delete('/blocked')
@jwt_required()
def delete_blocked_users():
    claims = get_jwt()
    if int(claims.get("permission", 0)) > 2:
        try:
            # Get all blocked users
            blocked_users = User.find_all({"blocked": True})
            
            deleted_count = 0
            for user in blocked_users:
                try:
                    # Check if user has active orders
                    from models import Order, Cart
                    
                    user_carts = Cart.find_all({"user_id": user._id})
                    cart_ids = [cart._id for cart in user_carts]
                    
                    if cart_ids:
                        active_orders = Order.find_all({
                            "cart_id": {"$in": cart_ids},
                            "status": {"$nin": ["COMPLETED", "CANCELLED"]}
                        })
                        
                        if active_orders:
                            continue  # Skip this user if they have active orders
                    
                    # Delete user and their data
                    user.delete()
                    
                    # Delete user's carts
                    for cart in user_carts:
                        cart.delete()
                    
                    # Delete user's completed orders
                    if cart_ids:
                        completed_orders = Order.find_all({
                            "cart_id": {"$in": cart_ids},
                            "status": {"$in": ["COMPLETED", "CANCELLED"]}
                        })
                        for order in completed_orders:
                            order.delete()
                    
                    deleted_count += 1
                    
                except Exception as user_error:
                    print(f"Error deleting user {user._id}: {str(user_error)}")
                    continue
            
            return jsonify({
                "message": f"DELETED_{deleted_count}_BLOCKED_USERS"
            }), 200
            
        except Exception as e:
            return jsonify({"error": f"Error deleting blocked users: {str(e)}"}), 500
    else:
        return jsonify({"error": "FORBIDDEN"}), 403
