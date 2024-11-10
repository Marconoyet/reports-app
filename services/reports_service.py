
from pptx import Presentation
from io import BytesIO
from db.reports import get_report_db
import base64
import re
from spire.pdf.common import *
from spire.pdf import *
from io import BytesIO
import fitz
from db.custom_exceptions import DatabaseError
from db.reports import (
    add_report_db,
    get_report_db,
    delete_report_db,
    update_report_db,
    get_file_of_report
)
from db.files import upload_file_db
from sqlalchemy.exc import SQLAlchemyError
from services.services_utiliy import extract_first_image_from_slide
from datetime import datetime
import threading
from flask import current_app


def allowed_file(filename):
    allowed_extensions = {'pptx'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions


def add_report(report_data):
    """Business logic for adding a report and saving the first image from the first slide in the template."""
    try:
        file = report_data.get('file')

        print("File saved as report.pptx")
        if file and allowed_file(file.filename):
            # Step 1: Extract the first image from the first slide
            file_binary_data = file.read()
            file_stream = BytesIO(file_binary_data).getvalue()
            first_image_stream = extract_first_image_from_slide(file)

            # Step 2: Convert the image to binary data
            image_bytes = first_image_stream.getvalue()

            # Step 3: Insert report metadata into MySQL
            report_metadata = {
                "template_name": report_data.get('reportName'),
                "template_description": report_data.get('reportDescription'),
                "template_image": image_bytes,
                "user_id": int(report_data.get('userId')),
                "folder_id": int(report_data.get('folderId')),
                "center_id": int(report_data.get('centerId')),
                "template_file": file_stream,
                "created_time": datetime.now()
            }

            # Step 4: Insert the report into the MySQL database
            report_id = add_report_db(report_metadata)

            return {"status": "success", "report_id": report_id}

        else:
            raise Exception("Invalid file type or no file uploaded.")

    except SQLAlchemyError as e:
        raise Exception(f"Database operation failed: {e}")

    except Exception as e:
        raise Exception(f"Service Error - Could not add report: {e}")


def get_report(report_id):
    """Business logic for retrieving a report."""
    try:
        return get_report_db(report_id)
    except DatabaseError as e:
        raise Exception(f"Service Error - Could not retrieve report: {e}")


def delete_report(report_id):
    """Business logic for deleting a report."""
    try:
        return delete_report_db(report_id)
    except DatabaseError as e:
        raise Exception(f"Service Error - Could not delete report: {e}")


def update_report(report_id, updated_data):
    """Business logic for deleting a report."""
    try:
        return update_report_db(report_id, updated_data)
    except DatabaseError as e:
        raise Exception(f"Service Error - Could not delete report: {e}")


def generate_pptx_report(replacements, report_id, report_name):
    report = get_file_of_report(report_id)
    file_data = report.template_file
    presentation = Presentation(BytesIO(file_data))

    # Replace the fields in the PPTX
    for slide in presentation.slides:
        for shape in slide.shapes:
            if not hasattr(shape, "text_frame"):
                continue
            for paragraph in shape.text_frame.paragraphs:
                for run in paragraph.runs:
                    for key, value in replacements.items():
                        if key in run.text:
                            run.text = run.text.replace(key, value)

    # Save the modified presentation to a BytesIO stream
    output_stream = BytesIO()
    presentation.save(output_stream)
    output_stream.seek(0)

    # Start a background thread to handle the file upload process
    app = current_app._get_current_object()
    threading.Thread(target=upload_pptx_in_background,
                     args=(output_stream, report, app, report_name)).start()

    # Return the stream to the client
    return output_stream


def upload_pptx_in_background(output_stream, report, app, report_name):
    # Prepare the report for upload
    # Read the stream into binary for upload
    report.template_file = output_stream.getvalue()
    neededData = prepareReportForUpload(report, report_name)

    # Upload the file to the database in a background thread

    # Run the upload process inside the app context
    with app.app_context():
        try:
            upload_response = upload_file_db(neededData)
            print(f"File upload successful: {upload_response}")
        except Exception as e:
            print(f"Error uploading file in background: {e}")


def prepareReportForUpload(report, report_name):
    try:
        # Try to convert the report to a dictionary
        report_data = report.to_dict()
    except AttributeError as e:
        print(f"Error converting report to dictionary: {e}")
        raise Exception(f"Error converting report to dictionary: {e}")

    try:
        # Extract the file from the report
        file = report.template_file
        if not file:
            print("The report has no associated template file.")
            raise ValueError("The report has no associated template file.")
        if isinstance(file, bytes):
            file_binary_data = file
            # Wrap bytes in BytesIO for further operations
            file_io = BytesIO(file_binary_data)
        else:
            raise ValueError("Unexpected file format")
        first_image_stream = extract_first_image_from_slide(file_io)
        image_bytes = first_image_stream.getvalue()
    except AttributeError as e:
        print(
            f"Error accessing the report file or file-related attributes: {e}")
        raise Exception(
            f"Error accessing the report file or file-related attributes: {e}")
    except Exception as e:
        print(f"Error processing the template file: {e}")
        raise Exception(f"Error processing the template file: {e}")

    try:
        # Prepare the report metadata
        report_metadata = {
            "report_name": report_name,  # Report name
            "template_id": report_data.get("id"),  # Template ID (foreign key)
            "report_file": file_binary_data,                            # Binary file data
            "report_image": image_bytes,
            "center_id": report_data.get("center_id"),
            "user_id": report_data.get("user_id"),
            "created_time": datetime.now()                  # Current timestamp
        }

        return report_metadata

    except KeyError as e:
        print(e)
        raise Exception(f"Missing required report data: {e}")
    except Exception as e:
        print(e)
        raise Exception(
            f"An unexpected error occurred while preparing report metadata: {e}")


def get_report_and_extract_fields(report_id):
    """Service layer to extract fields from PPTX or PDF files."""
    try:
        # Retrieve the report data and file from the database
        # report_data = get_report_db(report_id)
        # file_id = str(report_data["fileId"])
        # if not report_data or not report_data.get("fileId"):
        #     raise Exception("Report or file not found")

        # file_type = report_data.get("fileName").split('.')[-1].lower()
        # if file_type == 'pptx':
        #     fields = extract_pptx_fields(report_id)
        # else:
        #     raise Exception(f"Unsupported file type: {file_type}")
        fields = extract_pptx_fields(report_id)
        return fields
    except Exception as e:
        raise Exception(f"Service Error - Could not extract fields: {e}")


def extract_pptx_fields(report_id):
    """Extract fields from a PPTX file."""
    report = get_file_of_report(report_id)
    file_data = report.template_file
    presentation = Presentation(BytesIO(file_data))
    fields = []
    for slide in presentation.slides:
        for shape in slide.shapes:
            if hasattr(shape, "text_frame"):
                for paragraph in shape.text_frame.paragraphs:
                    for run in paragraph.runs:
                        if "#" in run.text:  # Assume fields start with '#'
                            fields.append(run.text)
    report_data = report.to_dict()
    if report.template_image:
        encoded_image = base64.b64encode(report.template_image).decode('utf-8')
        report_data['template_image'] = f"data:image/png;base64,{encoded_image}"
    combined_data = {
        "report": report_data,            # Folder details
        "fields": fields  # Templates associated with the folder
    }
    return combined_data


def remove_non_english(text):
    # Use regex to find and keep only English letters, numbers, and spaces
    cleaned_text = re.sub(r'[^a-zA-Z0-9#_ ]', '', text)
    return cleaned_text


def extract_pdf_fields(file_id):
    """Extract fields from a PDF file stored in GridFS."""
    pdf_data = get_file_from_gridfs(
        file_id)  # Function to retrieve PDF from GridFS
    pdf_stream = BytesIO(pdf_data)

    # Open the PDF file with fitz (PyMuPDF)
    document = fitz.open(stream=pdf_stream, filetype="pdf")
    fields = []

    # Loop through each page of the PDF
    for page_num in range(document.page_count):
        page = document.load_page(page_num)  # Load each page
        text = page.get_text("text")  # Extract plain text from the page

        # Print for debugging

        # Add logic to find specific markers in the PDF text (e.g., #field_name)
        for line in text.splitlines():
            if "#" in line:
                fields.append(remove_non_english(line.strip()))

    document.close()
    return fields
