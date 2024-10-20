from flask import Blueprint, request, jsonify, send_file
from services.reports_service import add_report, get_report, delete_report
from services.reports_service import generate_pptx_report, get_report_and_extract_fields
reports_bp = Blueprint('reports', __name__)


@reports_bp.route('/create', methods=['POST'])
def create_new_report():
    try:
        # Handle form and file data from the request
        report_name = request.form.get('reportName')
        report_description = request.form.get('reportDescription')
        folder_id = request.form.get('folderId')
        file = request.files.get('file')  # Get the file from the request
        userId = request.form.get('userId')  
        folderId = request.form.get('folderId')  
        # Prepare the data to pass to the service layer
        data = {
            "reportName": report_name,
            "reportDescription": report_description,
            "folderId": folder_id,
            "file": file ,
            "userId":userId,
            "folderId": folderId
        }

        # Call the service layer to handle business logic
        report_id = add_report(data)

        return jsonify({"status": "success", "report_id": report_id}), 201
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@reports_bp.route('/<report_id>', methods=['GET'])
def get_report_data(report_id):
    try:
        report = get_report(report_id)
        if not report:
            return jsonify({"status": "error", "message": "Report not found"}), 404
        return jsonify({"status": "success", "data": report}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@reports_bp.route('/<report_id>', methods=['DELETE'])
def delete_report_data(report_id):
    try:
        delete_report(report_id)
        return jsonify({"status": "success", "message": "Report deleted successfully"}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@reports_bp.route('/<string:report_id>/extract-fields', methods=['GET'])
def extract_fields(report_id):
    try:
        fields = get_report_and_extract_fields(report_id)
        return jsonify({"status": "success", "data": fields, "report_id":report_id}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@reports_bp.route('/generate', methods=['POST'])
def generate_report_api():
    try:
        data = request.json
        report_id = data.get('report_id')
        filetype = data.get('filetype')
        # Check file extension and handle accordingly
        if filetype.endswith('pptx'):
            pptx_data = generate_pptx_report(data['replacements'], report_id)
            return send_file(pptx_data, as_attachment=True, download_name="modified_presentation.pptx")
        else:
            return jsonify({"status": "error", "message": "Unsupported file type"}), 400
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


# @reports_bp.route('/<report_id>/extract-fields', methods=['GET'])
# def extract_fields(report_id):
#     try:
#         print(report_id)
#         result = get_report_and_extract_fields(report_id)
#         return jsonify({"status": "success", "fields": result}), 200
#     except Exception as e:
#         return jsonify({"status": "error", "message": str(e)}), 500

# # Endpoint to generate the report and send back the modified PPTX
# @reports_bp.route('/generate', methods=['POST'])
# def generate_report_api():
#     try:
#         data = request.json
#         pptx_data = generate_report(data['replacements'], data['filename'])
#         return send_file(pptx_data, as_attachment=True, download_name="modified_presentation.pptx")
#     except Exception as e:
#         return jsonify({"status": "error", "message": str(e)}), 500
