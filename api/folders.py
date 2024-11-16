from flask import Blueprint, request, jsonify
from services.folders_service import (
    create_folder,
    get_folder,
    update_folder,
    delete_folder,
    list_folders
)
from services.users_service import get_user_role
from flask_jwt_extended import (
    jwt_required,
    get_jwt_identity,
)
folders_bp = Blueprint('folders', __name__)


@folders_bp.route('/create', methods=['POST'])
@jwt_required()  # Assuming JWT for authentication
def create_new_folder():
    try:
        data = request.json
        current_user_id = get_jwt_identity()
        # Assume this fetches the user details including role and center_id
        user = get_user_role(current_user_id)
        role = user.get('role')
        # Center ID filtering for non-SuperAdmins
        center_id = user.get('center_id') if role != 'SuperAdmin' else None
        folder_id = create_folder(data, center_id, role)
        return jsonify({"status": "success", "folder_id": folder_id}), 201
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@folders_bp.route('/<folder_id>', methods=['GET'])
def get_folder_data(folder_id):
    try:
        folder = get_folder(folder_id)
        if not folder:
            return jsonify({"status": "error", "message": "Folder not found"}), 404
        return jsonify({"status": "success", "data": folder}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@folders_bp.route('/<folder_id>', methods=['PUT'])
def update_folder_data(folder_id):
    try:
        data = request.json
        update_folder(folder_id, data)
        return jsonify({"status": "success", "message": "Folder updated successfully"}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@folders_bp.route('/<folder_id>', methods=['DELETE'])
def delete_folder_data(folder_id):
    try:
        delete_folder(folder_id)
        return jsonify({"status": "success", "message": "Folder deleted successfully"}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@folders_bp.route('/list', methods=['GET'])
@jwt_required()
def list_folders_data():
    try:
        current_user_id = get_jwt_identity()
        user = get_user_role(current_user_id)
        role = user.get('role')
        # Center ID filtering for non-SuperAdmins
        center_id = user.get('center_id') if role != 'SuperAdmin' else None
        folders = list_folders(role, center_id)
        return jsonify({"status": "success", "data": folders}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
