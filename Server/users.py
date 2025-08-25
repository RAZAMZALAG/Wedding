from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt
from models import User, db
from schemas import ManagedUserSchema, UserIdFileSchema
from validation import is_valid_permission

user_bp = Blueprint("users", __name__)


@user_bp.get('/')
@jwt_required()
def get_all_users():
    claims = get_jwt()
    if int(claims.get("permission", 0)) > 2:
        page = request.args.get("page", default=1, type=int)
        per_page = request.args.get("per_page", default=20, type=int)
        blocked_param = request.args.get("blocked", default="0", type=str)
        # Convert to boolean - "0" or "false" means False, anything else means True
        blocked = blocked_param.lower() in ["1", "true", "yes"]
        order_by = request.args.get("order_by", default=None, type=str)
        direction = request.args.get("direction", default="asc", type=str)

        query = User.query.filter(User.blocked == blocked)

        # Add sorting logic
        if order_by:
            # Map frontend field names to model attributes
            order_map = {
                "name": (User.first_name, User.last_name),
                "email": User.email,
                "phone_number": User.phone_number,
                "location": User.location,
                "id_file": User.id_file,
            }
            if order_by in order_map:
                col = order_map[order_by]
                if isinstance(col, tuple):
                    # Sort by first_name, then last_name
                    if direction == "desc":
                        query = query.order_by(col[0].desc(), col[1].desc())
                    else:
                        query = query.order_by(col[0].asc(), col[1].asc())
                else:
                    if direction == "desc":
                        query = query.order_by(col.desc())
                    else:
                        query = query.order_by(col.asc())

        users = query.paginate(page=page, per_page=per_page)
        result = ManagedUserSchema().dump(users, many=True)
        return jsonify({
            "users": result,
            "meta": {
                "total_users": users.total,
                "total_pages": users.pages,
                "current_page": users.page,
                "per_page": per_page
            }
        }), 200
    return jsonify({"error": "UNAUTHORIZED"}), 401


@user_bp.get('id/<user_id>')
@jwt_required()
def get_user_id_file(user_id):
    claims = get_jwt()
    if int(claims.get("permission", 0)) > 2:
        user = User.query.get(user_id)
        if not user:
            return jsonify({"error": "USER_NOT_FOUND"}), 404

        if not user.id_file:
            return jsonify({"error": "NO_ID_FILE"}), 404

        serialized = UserIdFileSchema().dump(user)
        return jsonify(serialized), 200

    return jsonify({"error": "UNAUTHORIZED"}), 401


from validation import is_valid_username, is_valid_email, is_valid_location, is_valid_phone


@user_bp.put('/update/<user_id>')
@jwt_required()
def update_user(user_id):
    claims = get_jwt()
    if int(claims.get("permission", 0)) <= 2:
        return jsonify({"error": "UNAUTHORIZED"}), 401

    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'USER_NOT_FOUND'}), 404

    # Prevent changing admin's permission
    if user.permission == 3:
        if 'permission' in request.get_json() or 'blocked' in request.get_json():
            return jsonify({'error': 'CANNOT_MODIFY_ADMIN'}), 403

    data = request.get_json()
    if not data:
        return jsonify({'error': 'NO_DATA_PROVIDED'}), 400

    # Allowed fields to update
    allowed_fields = {
        'first_name': is_valid_username,
        'last_name': is_valid_username,
        'email': is_valid_email,
        'phone_number': is_valid_phone,
        'location': is_valid_location,
        'permission': is_valid_permission,
    }

    for field, validator in allowed_fields.items():
        if field in data:
            value = data[field]
            error = validator(value)
            if error:
                return error  # return the first validation error
            setattr(user, field, value)

    user.save()
    return jsonify({'message': 'USER_UPDATED'}), 200


@user_bp.put('/block/<user_id>')
@jwt_required()
def block_user(user_id):
    claims = get_jwt()
    if int(claims.get("permission", 0)) < 2:
        return jsonify({"error": "UNAUTHORIZED"}), 401

    data = request.get_json()
    if not data or "block" not in data:
        return jsonify({"error": "MISSING_BLOCK_STATUS"}), 400

    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "USER_NOT_FOUND"}), 404

    # Prevent blocking admin
    if user.permission == 3:
        return jsonify({"error": "CANNOT_BLOCK_ADMIN"}), 403

    block = data["block"]
    if not isinstance(block, bool):
        return jsonify({"error": "BLOCK_MUST_BE_BOOLEAN"}), 400

    user.blocked = block
    user.save()

    return jsonify({
        "message": "USER_BLOCKED" if block else "USER_UNBLOCKED"
    }), 200


@user_bp.delete('/delete-non-admins')
@jwt_required()
def delete_non_admin_users():
    """מחיקת כל המשתמשים חוץ מאדמינים (הרשאה 3)"""
    claims = get_jwt()
    if int(claims.get("permission", 0)) < 3:
        return jsonify({"error": "INSUFFICIENT_PERMISSION"}), 403
    
    try:
        # מוצא כל המשתמשים שאינם אדמינים
        non_admin_users = User.query.filter(User.permission < 3).all()
        
        if not non_admin_users:
            return jsonify({"message": "NO_NON_ADMIN_USERS_FOUND"}), 200
        
        deleted_count = 0
        for user in non_admin_users:
            # בדיקה נוספת לוודא שזה לא אדמין
            if user.permission < 3:
                db.session.delete(user)
                deleted_count += 1
        
        db.session.commit()
        
        return jsonify({
            "message": "NON_ADMIN_USERS_DELETED",
            "deleted_count": deleted_count
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"DELETE_FAILED: {str(e)}"}), 500


@user_bp.delete('/<user_id>')
@jwt_required()
def delete_user(user_id):
    """מחיקת משתמש בודד"""
    claims = get_jwt()
    if int(claims.get("permission", 0)) < 3:
        return jsonify({"error": "INSUFFICIENT_PERMISSION"}), 403
    
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "USER_NOT_FOUND"}), 404
        
    # מניעת מחיקת אדמין
    if user.permission == 3:
        return jsonify({"error": "CANNOT_DELETE_ADMIN"}), 403
    
    try:
        db.session.delete(user)
        db.session.commit()
        return jsonify({"message": "USER_DELETED"}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"DELETE_FAILED: {str(e)}"}), 500
