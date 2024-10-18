# import comtypes.client
import os
from db.files import (
    get_file_db,
    upload_file_db,
    move_file_db,
    delete_file_db,
    get_latest_reports
)
from db.custom_exceptions import DatabaseError

from io import BytesIO
# import pythoncom
import tempfile


def get_file_service(report_Id):
    """Business logic for uploading a file to a folder."""
    try:
        report = get_file_db(report_Id)
        report.report_file = BytesIO(report.report_file)
        return report.report_name, report.report_file
        # pdf_file = convert_pptx_to_pdf(report.report_file)
        # return report.report_name, report.report_file, pdf_file
    except DatabaseError as e:
        print(e)
        raise Exception(f"Service Error - Could not upload file: {e}")


# def convert_pptx_to_pdf(pptx_binary_data):
#     """Convert PPTX binary data to PDF using comtypes and return as BytesIO."""
#     # Initialize the COM library
#     pythoncom.CoInitialize()

#     # Create a temporary file to hold the pptx binary data
#     with tempfile.NamedTemporaryFile(suffix=".pptx", delete=False) as temp_pptx_file:
#         temp_pptx_file.write(pptx_binary_data)
#         temp_pptx_path = temp_pptx_file.name  # Get the file path

#     # Create a temporary file for the output PDF
#     with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as temp_pdf_file:
#         temp_pdf_path = temp_pdf_file.name

#     try:
#         # Start PowerPoint application
#         powerpoint = comtypes.client.CreateObject("Powerpoint.Application")
#         powerpoint.Visible = 1

#         # Open the temporary PPTX file
#         presentation = powerpoint.Presentations.Open(temp_pptx_path)

#         # Save as PDF
#         presentation.SaveAs(temp_pdf_path, 32)  # 32 is the format for PDF

#         # Close the presentation and quit PowerPoint
#         presentation.Close()
#         powerpoint.Quit()

#         # Read the PDF data from the temporary file
#         with open(temp_pdf_path, "rb") as pdf_file:
#             pdf_data = BytesIO(pdf_file.read())

#     finally:
#         # Clean up the temporary files
#         os.remove(temp_pptx_path)
#         os.remove(temp_pdf_path)
#         # Uninitialize the COM library
#         pythoncom.CoUninitialize()
#     return pdf_data


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


def delete_file(file_id, folder_id):
    """Business logic for deleting a file from a folder."""
    try:
        return delete_file_db(file_id, folder_id)
    except DatabaseError as e:
        raise Exception(f"Service Error - Could not delete file: {e}")


def get_files(limit):
    """Business logic for deleting a file from a folder."""
    try:
        return get_latest_reports(limit)
    except DatabaseError as e:
        raise Exception(f"Service Error - Could not delete file: {e}")
