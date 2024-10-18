from flask import Blueprint, request, jsonify
from services.folders_service import (
    create_folder,
    get_folder,
    update_folder,
    delete_folder,
    list_folders
)

folders_bp = Blueprint('folders', __name__)


@folders_bp.route('/create', methods=['POST'])
def create_new_folder():
    try:
        data = request.json
        folder_id = create_folder(data)
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
def list_folders_data():
    try:
        folders = list_folders()
        return jsonify({"status": "success", "data": folders}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
