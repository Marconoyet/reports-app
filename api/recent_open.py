from flask import Blueprint, request, jsonify
from services.recent_open_service import (
    add_recent_open,
    list_recent_open,
    clear_recent_open
)

recent_open_bp = Blueprint('recent_open', __name__)


@recent_open_bp.route('/add', methods=['POST'])
def add_new_recent_open():
    try:
        recent_open_data = request.json
        recent_open_id = add_recent_open(recent_open_data)
        return jsonify({"status": "success", "recent_open_id": recent_open_id}), 201
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@recent_open_bp.route('/list', methods=['GET'])
def get_recent_open_list():
    try:
        user_id = request.args.get('user_id')
        recent_open_list = list_recent_open(user_id)
        return jsonify({"status": "success", "data": recent_open_list}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@recent_open_bp.route('/clear', methods=['DELETE'])
def clear_all_recent_open():
    try:
        cleared_count = clear_recent_open()
        return jsonify({"status": "success", "message": f"{cleared_count} entries cleared"}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
