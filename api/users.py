from flask import Blueprint, request, jsonify
from services.users_service import create_user, get_user, update_user, delete_user, list_users

users_bp = Blueprint('users', __name__)


@users_bp.route('/create', methods=['POST'])
def create_new_user():
    try:
        data = request.json
        user_id = create_user(data)
        return jsonify({"status": "success", "user_id": user_id}), 201
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@users_bp.route('/<user_id>', methods=['GET'])
def get_user_data(user_id):
    try:
        user = get_user(user_id)
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
def list_users_data():
    try:
        users = list_users()
        return jsonify({"status": "success", "data": users}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
