from flask_jwt_extended import (
    jwt_required,
    get_jwt_identity,
)
from services.users_service import get_user_role
from flask import Blueprint, request, jsonify, send_file
from services.files_service import get_file_service, move_file, delete_file, get_files, get_file_pdf_service, modify_pdf_metadata
files_bp = Blueprint('files', __name__)


@files_bp.route('/<int:report_id>', methods=['GET'])
def get_file(report_id):
    try:

        report_name, pptx_data = get_file_service(report_id)
        response = send_file(pptx_data, as_attachment=False,
                             download_name=f"{report_name}.xml")
        # Set content-disposition header with filename manually if not set
        response.headers["Content-Disposition"] = f'attachment; filename="{report_name}.xml"'
        # Expose headers for CORS if necessary
        response.headers["Access-Control-Expose-Headers"] = "Content-Disposition"
        return response

    except Exception as e:
        print(e)
        return jsonify({"status": "error", "message": str(e)}), 500


@files_bp.route('/pdf/<int:report_id>', methods=['GET'])
def get_file_pdf(report_id):
    try:
        result = get_file_pdf_service(report_id)
        if "error" in result:
            return jsonify({"status": "error", "message": result["error"]}), 500
        afterEditStream = modify_pdf_metadata(
            result["pdf_stream"], result["report_name"])
        return send_file(afterEditStream, mimetype='application/pdf',
                         as_attachment=True, download_name=f'{result["report_name"]}.pdf')
        # # Set content-disposition header with filename manually if not set
        # response.headers["Content-Disposition"] = f'attachment; filename="{result["report_name"]}.pdf"'
        # # Expose headers for CORS if necessary
        # response.headers["Access-Control-Expose-Headers"] = "Content-Disposition"
        # return response
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@files_bp.route('/move', methods=['POST'])
def move_file_to_folder():
    try:
        file_id = request.json.get('file_id')
        from_folder = request.json.get('from_folder')
        to_folder = request.json.get('to_folder')
        move_file(file_id, from_folder, to_folder)
        return jsonify({"status": "success", "message": "File moved successfully"}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@files_bp.route('/<file_id>', methods=['DELETE'])
def delete_file_data(file_id):
    try:
        delete_file(file_id)
        return jsonify({"status": "success", "message": "File deleted successfully"}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@files_bp.route('/get_list', methods=['GET'])
@jwt_required()
def get_files_paginated():
    try:
        current_user_id = get_jwt_identity()
        user = get_user_role(current_user_id)
        role = user.get('role')
        center_id = user.get('center_id') if role != 'SuperAdmin' else None
        limit = int(request.args.get('limit', 10))
        page = int(request.args.get('page', 1))
        files, total_records = get_files(limit, page, center_id)
        return jsonify({
            "status": "success",
            "message": "Files retrieved successfully",
            "files": files,
            "total_records": total_records  # Include total records for frontend
        }), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
