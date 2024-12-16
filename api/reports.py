import os
from flask import current_app
from io import BytesIO
from flask import Blueprint, request, jsonify, send_file
import zipfile
from services.reports_service import generate_pptx_report, process_rar_file, process_zip_file, get_report_and_extract_fields, handle_extract_xml_fields, generate_xml_report, add_report, get_report, delete_report, update_report, add_report_xml
from services.files_service import modify_pdf_metadata, create_file_service
from db.files import update_file_db
from datetime import datetime
import base64
import io
import threading
from werkzeug.utils import secure_filename
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
        centerId = request.form.get('centerId')
        # Prepare the data to pass to the service layer
        data = {
            "reportName": report_name,
            "reportDescription": report_description,
            "folderId": folder_id,
            "file": file,
            "userId": userId,
            "folderId": folderId,
            "centerId": centerId
        }

        # Call the service layer to handle business logic
        report_id = add_report(data)

        return jsonify({"status": "success", "report_id": report_id}), 201
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@reports_bp.route('/create-xml', methods=['POST'])
def create_new_report_xml():
    try:
        # Handle form and file data from the request
        report_name = request.form.get('reportName')
        report_description = request.form.get('reportDescription')
        folder_id = request.form.get('folderId')
        file = request.files.get('file')  # Get the file from the request
        userId = request.form.get('userId')
        centerId = request.form.get('centerId')
        template_image = request.form.get("templateImg")
        if template_image:
            # Extract the base64 portion after the comma
            base64_data = template_image.split(",")[1]
            image_binary_data = base64.b64decode(base64_data)
        else:
            image_binary_data = None

        data = {
            "template_name": report_name,
            "template_description": report_description,
            "template_image": image_binary_data,
            "folder_id": int(folder_id),
            "template_file": file.read(),
            "user_id": int(userId),
            "center_id": int(centerId),
            "created_time": datetime.now()
        }
        report_id = add_report_xml(data)
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


def run_in_app_context(app, func, *args, **kwargs):
    """
    Runs a function inside the given Flask application context.
    """
    with app.app_context():  # Use the passed app to create the context
        func(*args, **kwargs)


@reports_bp.route('/<report_id>', methods=['PUT'])
def update_report_data(report_id):
    try:
        viewer = request.args.get('viewer', 'false')
        is_viewer = viewer.lower() == 'true'
        if not request.content_type.startswith('multipart/form-data'):
            raise Exception(
                "Invalid Content-Type. Expected multipart/form-data")

        # Extract file and form data
        file = request.files.get('template_file')  # Get the uploaded file
        if not file:
            raise Exception("No file provided in the request")
        file_content = file.read()  # Read file content

        report_name = request.form.get("reportName")  # Get report name

        saving = request.form.get("saving", type=bool)  # Get saving flag

        if saving and not is_viewer:
            app = current_app._get_current_object()  # Pass the actual Flask app
            thread = threading.Thread(target=run_in_app_context, args=(app, create_file_service, report_id, {
                "template_file": file_content,
                "report_name": report_name
            }))
            thread.start()
        # Update the database with the file content
        if is_viewer:
            updated_data = {"report_file": file_content}
            update_file_db(report_id, updated_data)
        else:
            updated_data = {"template_file": file_content}
            update_report(report_id, updated_data)
        return jsonify({"status": "success", "message": "Report updated successfully"}), 200

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@reports_bp.route('/<report_id>', methods=['DELETE'])
def delete_report_data(report_id):
    try:
        delete_report(report_id)
        return jsonify({"status": "success", "message": "Report deleted successfully"}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@reports_bp.route('/<string:report_id>/extract-xml-fields', methods=['GET'])
def extract_xml_fields(report_id):
    try:
        # Get `viewer` query parameter
        viewer = request.args.get('viewer', 'false')
        is_viewer = viewer.lower() == 'true'          # Convert to boolean
        fields = handle_extract_xml_fields(report_id, is_viewer)
        return jsonify({"status": "success", "data": fields, "report_id": report_id}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@reports_bp.route('/<string:report_id>/extract-fields', methods=['GET'])
def extract_fields(report_id):
    try:
        fields = get_report_and_extract_fields(report_id)
        return jsonify({"status": "success", "data": fields, "report_id": report_id}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@reports_bp.route('/process-zip', methods=['POST'])
def process_zip():
    try:
        uploaded_file = request.files.get('file')
        if not uploaded_file:
            return jsonify({"status": "error", "message": "No file uploaded"}), 400

        # Check MIME type
        allowed_mime_types = [
            "application/zip",
            "application/x-compressed",
            "application/x-zip-compressed"
        ]
        if uploaded_file.mimetype not in allowed_mime_types:
            # Fallback: Check file extension
            if not uploaded_file.filename.endswith('.zip'):
                return jsonify({"status": "error", "message": "Invalid file type. Only .zip files are allowed."}), 400

        # Process the file as ZIP
        processed_html = process_zip_file(uploaded_file)

        return send_file(
            io.BytesIO(processed_html.encode('utf-8')),
            mimetype="text/html",
            as_attachment=True,
            download_name="processed_report.html"
        )
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@reports_bp.route('/generate-xml', methods=['POST'])
def generate_report_xml():
    try:
        data = request.json
        report_id = data.get('report_id')
        report_name = data.get('report_name')
        replacements = data['replacements']
        modified_file_stream = generate_xml_report(
            replacements, report_id, report_name)

        # Return the modified file
        return send_file(
            modified_file_stream,
            mimetype="text/xml",
            as_attachment=True,
            download_name=f"{report_name}.xml"
        )
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@reports_bp.route('/generate', methods=['POST'])
def generate_report_api():
    try:
        data = request.json
        report_id = data.get('report_id')
        report_name = data.get('report_name')
        filetype = data.get('filetype')
        if filetype.endswith('pptx'):
            pptx_stream, pdf_stream, pdf_error = generate_pptx_report(
                data['replacements'], report_id, report_name
            )

            pdf_stream = modify_pdf_metadata(
                pdf_stream, report_name)

            if pdf_error:
                return jsonify({"status": "error", "message": pdf_error}), 500

            zip_stream = BytesIO()
            with zipfile.ZipFile(zip_stream, 'w') as zip_file:
                zip_file.writestr("modified_presentation.pptx",
                                  pptx_stream.getvalue())
                if pdf_stream:
                    zip_file.writestr(
                        "converted_presentation.pdf", pdf_stream.getvalue())
            zip_stream.seek(0)

            return send_file(
                zip_stream,
                as_attachment=True,
                download_name="report_files.zip",
                mimetype='application/zip'
            )
        else:
            return jsonify({"status": "error", "message": "Unsupported file type"}), 400
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
