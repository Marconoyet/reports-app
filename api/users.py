from flask import Blueprint, request, jsonify
from services.users_service import create_user, get_user, update_user, delete_user, list_users, check_users_email, check_users_username, check_users_login, get_user_role
from flask_jwt_extended import (
    jwt_required,
    get_jwt_identity,
)
users_bp = Blueprint('users', __name__)


@users_bp.route('/create', methods=['POST'])
@jwt_required()
def create_new_user():
    try:
        data = request.json
        current_user_id = get_jwt_identity()
        # Assume this fetches the user details including role and center_id
        user = get_user_role(current_user_id)
        role = user.get('role')
        center_id = user.get(
            'center_id') if role != 'SuperAdmin' else data.get("center")
        user = create_user(data, center_id)
        return jsonify({"status": "success", "user": user}), 201
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@users_bp.route('/<user_id>', methods=['GET'])
def get_user_data(user_id):
    try:
        include_password = request.args.get(
            'password', 'false').lower() == 'true'
        user = get_user(user_id, include_password)
        if not user:
            return jsonify({"status": "error", "message": "User not found"}), 404
        return jsonify({"status": "success", "data": user}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@users_bp.route('/<user_id>', methods=['PUT'])
def update_user_data(user_id):
    try:
        data = request.json
        update_user(user_id, data)
        return jsonify({"status": "success", "message": "User updated successfully"}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@users_bp.route('/<user_id>', methods=['DELETE'])
def delete_user_data(user_id):
    try:
        delete_user(user_id)
        return jsonify({"status": "success", "message": "User deleted successfully"}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@users_bp.route('/list', methods=['GET'])
@jwt_required()
def list_users_data():
    try:
        current_user_id = get_jwt_identity()
        # Assume this fetches the user details including role and center_id
        user = get_user_role(current_user_id)
        role = user.get('role')
        center_id = user.get('center_id') if role != 'SuperAdmin' else None
        users = list_users(center_id)
        return jsonify({"status": "success", "data": users}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@users_bp.route('/auth-user', methods=['POST'])
def check_credentials():
    try:
        data = request.json
        user = data.get("username_or_email")
        password = data.get("password")
        users = check_users_login(user, password)
        return jsonify({"status": "success", "data": users}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@users_bp.route('/check-username', methods=['POST'])
def check_username():
    """Check if a username is already taken."""
    try:
        username = request.json.get('username')
        if not username:
            return jsonify({"status": "error", "message": "Username is required"}), 400

        # Query the database to check if the username exists
        user = check_users_username(username)

        if user:
            return jsonify({"isAvailable": False}), 200  # Username is taken
        else:
            return jsonify({"isAvailable": True}), 200  # Username is available

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@users_bp.route('/check-email', methods=['POST'])
def check_email():
    """Check if an email is already in use."""
    try:
        email = request.json.get('email')
        if not email:
            return jsonify({"status": "error", "message": "Email is required"}), 400

        # Query the database to check if the email exists
        user = check_users_email(email)

        if user:
            return jsonify({"isAvailable": False}), 200  # Email is taken
        else:
            return jsonify({"isAvailable": True}), 200  # Email is available

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
