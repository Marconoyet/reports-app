# import comtypes.client
import os
import subprocess
import tempfile
from db.files import (
    get_file_db,
    upload_file_db,
    move_file_db,
    delete_file_db,
    get_latest_reports
)

from db.reports import get_file_of_report
from db.custom_exceptions import DatabaseError
import fitz  # PyMuPDF
from io import BytesIO
from datetime import datetime
import tempfile


def create_file_service(report_id, file_data):
    """Business logic for creating and saving a file."""
    try:
        # Fetch existing report metadata
        report = get_file_of_report(report_id)
        report_data = report.to_dict()
        report_name = file_data.get("report_name")
        if not report_name or report_name == 'undefined':
            report_name = report_data.get("template_name")

        # Prepare metadata for the file
        report_metadata = {
            "report_name": report_name,  # Name of the report
            # Template ID (foreign key)
            "template_id": report_data.get("id"),
            # Binary file content
            "report_file": file_data.get("template_file"),
            "center_id": report_data.get("center_id"),
            "user_id": report_data.get("user_id"),
            "created_time": datetime.now()                # Current timestamp
        }

        # Save file metadata to the database
        file_id = upload_file_db(report_metadata)
        print(f"File saved successfully with ID: {file_id}")

    except DatabaseError as e:
        print(e)
        print(f"Error in create_file_service: {e}")


def get_file_service(report_Id):
    try:
        report = get_file_db(report_Id)
        report.report_file = BytesIO(report.report_file)
        return report.report_name, report.report_file
    except DatabaseError as e:
        print(e)
        raise Exception(f"Service Error - Could not get file: {e}")


def get_file_pdf_service(report_id):
    try:
        # Step 1: Retrieve the PPTX data from the database
        report = get_file_db(report_id)
        if not report or not report.report_file:
            return {"error": "Report not found or no template file"}

        pptx_stream = BytesIO(report.report_file)

        # Step 2: Save the PPTX to a temporary file
        with tempfile.NamedTemporaryFile(suffix=".pptx", delete=False) as temp_pptx_file:
            temp_pptx_file.write(pptx_stream.getvalue())
            temp_pptx_path = temp_pptx_file.name

        pdf_stream = None

        # Step 3: Convert the PPTX to PDF using LibreOffice
        with tempfile.TemporaryDirectory() as temp_output_dir:
            try:
                env = os.environ.copy()
                env["PATH"] += os.pathsep + "/usr/bin"
                libreoffice_path = '/usr/bin/libreoffice'  # Adjust path if necessary
                command = [
                    libreoffice_path, '--headless', '--convert-to', 'pdf', temp_pptx_path, '--outdir', temp_output_dir
                ]
                subprocess.run(command, check=True, env=env)
                pdf_path = os.path.join(temp_output_dir, os.path.splitext(
                    os.path.basename(temp_pptx_path))[0] + ".pdf")

                # Step 4: Read the generated PDF into a BytesIO stream
                pdf_stream = BytesIO()
                with open(pdf_path, 'rb') as pdf_file:
                    pdf_stream.write(pdf_file.read())
                pdf_stream.seek(0)
            except (subprocess.CalledProcessError, FileNotFoundError) as e:
                return {"error": f"Error during conversion: {e}"}
            finally:
                # Step 5: Cleanup temporary PPTX file
                try:
                    os.remove(temp_pptx_path)
                except OSError as cleanup_error:
                    return {"error": f"Error cleaning up temporary file: {cleanup_error}"}

        # Step 6: Return the generated PDF stream if no error
        return {"pdf_stream": pdf_stream, "report_name": report.report_name}
    except Exception as e:
        return {"error": f"Error converting PPTX to PDF: {e}"}


def upload_file(folder_id, file_data):
    """Business logic for uploading a file to a folder."""
    try:
        return upload_file_db(folder_id, file_data)
    except DatabaseError as e:
        raise Exception(f"Service Error - Could not upload file: {e}")


def move_file(file_id, from_folder, to_folder):
    """Business logic for moving a file from one folder to another."""
    try:
        return move_file_db(file_id, from_folder, to_folder)
    except DatabaseError as e:
        raise Exception(f"Service Error - Could not move file: {e}")


def delete_file(file_id):
    """Business logic for deleting a file from a folder."""
    try:
        return delete_file_db(file_id)
    except DatabaseError as e:
        raise Exception(f"Service Error - Could not delete file: {e}")


def get_files(limit, page, center_id):
    """Business logic for deleting a file from a folder."""
    try:
        return get_latest_reports(limit, page, center_id)
    except DatabaseError as e:
        raise Exception(f"Service Error - Could not delete file: {e}")


def modify_pdf_metadata(pdf_stream, new_title):
    pdf_document = fitz.open("pdf", pdf_stream)
    pdf_document.set_metadata({"title": new_title})
    pdf_stream = BytesIO()
    pdf_document.save(pdf_stream)
    pdf_document.close()
    pdf_stream.seek(0)
    return pdf_stream
