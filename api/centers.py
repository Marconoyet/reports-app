from flask import Blueprint, request, jsonify
from services.centers_service import (
    create_center, get_center, update_center, delete_center, list_centers
)

centers_bp = Blueprint('centers', __name__)


@centers_bp.route('/create', methods=['POST'])
def create_new_center():
    try:
        data = request.json
        center_id = create_center(data)
        return jsonify({"status": "success", "center_id": center_id}), 201
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@centers_bp.route('/<center_id>', methods=['GET'])
def get_center_data(center_id):
    try:
        center = get_center(center_id)
        if not center:
            return jsonify({"status": "error", "message": "Center not found"}), 404
        return jsonify({"status": "success", "data": center}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@centers_bp.route('/<center_id>', methods=['PUT'])
def update_center_data(center_id):
    try:
        data = request.json
        update_center(center_id, data)
        return jsonify({"status": "success", "message": "Center updated successfully"}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@centers_bp.route('/<center_id>', methods=['DELETE'])
def delete_center_data(center_id):
    try:
        delete_center(center_id)
        return jsonify({"status": "success", "message": "Center deleted successfully"}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@centers_bp.route('/list', methods=['GET'])
def list_centers_data():
    try:
        centers = list_centers()
        return jsonify({"status": "success", "data": centers}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
