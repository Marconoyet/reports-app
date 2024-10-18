from flask import Blueprint, request, jsonify, send_file
from services.files_service import get_file_service, move_file, delete_file, get_files
files_bp = Blueprint('files', __name__)


@files_bp.route('/<int:report_id>', methods=['GET'])
def get_file(report_id):
    try:

        report_name, pptx_data = get_file_service(report_id)
        return send_file(pptx_data, as_attachment=False, download_name=f"{report_name}.pptx")
        # return_pdf = request.args.get("pdf", False, type=bool)
        # print(return_pdf)
        # report_name, pptx_data, pdf_file = get_file_service(report_id)
        # if return_pdf:
        #     return send_file(pdf_file, as_attachment=False, download_name=f"{report_name}.pdf")
        # else:
        #     return send_file(pptx_data, as_attachment=False, download_name=f"{report_name}.pptx")
    except Exception as e:
        print(e)
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
        folder_id = request.json.get('folder_id')
        delete_file(file_id, folder_id)
        return jsonify({"status": "success", "message": "File deleted successfully"}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@files_bp.route('/get_list', methods=['GET'])
def get_files_limit():
    try:
        limit = request.args.get('limit', 10)
        files = get_files(limit)
        return jsonify({"status": "success", "message": "Files retrieved successfully", "files": files}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
