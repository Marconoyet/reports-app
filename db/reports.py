from flask import current_app
from pymongo.errors import PyMongoError
from bson.objectid import ObjectId
from .custom_exceptions import DatabaseError
from models.template_model import Template
from sqlalchemy.exc import SQLAlchemyError
from db.db_utils import execute_query
from models.folder_model import Folder
from models.reports_model import Report
from sqlalchemy.orm import defer
from db import db
import base64


def add_report_db(report_data):
    """Insert a new report into the MySQL database using SQLAlchemy."""
    try:
        new_report_id = execute_query(
            'insert', model=Template, data=report_data)
        return new_report_id
    except SQLAlchemyError as e:
        raise DatabaseError(f"Database operation failed: {e}")
    except Exception as e:
        raise DatabaseError(f"An unexpected error occurred: {e}")


def add_report_xml_db(report_data):
    """Insert a new report into the MySQL database using SQLAlchemy."""
    try:
        new_report_id = execute_query(
            'insert', model=Template, data=report_data)
        return new_report_id
    except SQLAlchemyError as e:
        raise DatabaseError(f"Database operation failed: {e}")
    except Exception as e:
        raise DatabaseError(f"An unexpected error occurred: {e}")


def get_report_db(report_id):
    """Retrieve a report by its ID."""
    try:
        report = current_app.db.reports.find_one({"_id": ObjectId(report_id)})
        if not report:
            raise DatabaseError(f"Report with ID {report_id} not found")
        return report
    except PyMongoError as e:
        raise DatabaseError(f"Error retrieving report: {e}")
    except Exception as e:
        raise DatabaseError(f"An unexpected error occurred: {e}")


def update_report_db(report_id, updated_data):
    """Update report information by its ID."""
    try:

        # Decode the base64 template_image if present
        if "template_image" in updated_data and updated_data["template_image"]:
            base64_data = updated_data["template_image"].split(",")[1]
            updated_data["template_image"] = base64.b64decode(base64_data)

        filters = {'id': report_id}
        result = execute_query('update', model=Template,
                               data=updated_data, filters=filters)
        print("updated data")
        if result == "No records found to update":
            raise Exception(f"Report with ID {report_id} not found for update")
        return result

    except Exception as e:
        raise Exception(f"Failed to update report: {e}")


def delete_report_db(report_id):
    """Delete a report by its ID and clean up related foreign key dependencies."""
    try:
        # Start a transaction explicitly
        db.session.begin()

        # Delete dependent records in the Report table
        dependent_deleted = db.session.query(Report).filter_by(
            template_id=report_id).delete(synchronize_session=False)
        print(f"Dependent rows deleted: {dependent_deleted}")

        # Delete the main record in the Template table
        filters = {'id': int(report_id)}
        result = execute_query('delete', model=Template, filters=filters)
        print(f"Template deletion result: {result}")

        # If no main records were deleted, raise an exception
        if result == "No records found to delete":
            raise ValueError(
                f"Report with ID {report_id} not found for deletion")

        # Commit the transaction manually
        db.session.commit()

        return {"status": "success", "details": "Report and related dependencies deleted."}

    except SQLAlchemyError as e:
        db.session.rollback()  # Rollback transaction on failure
        # If a connection error occurred after successful deletion
        if "Lost connection" in str(e):
            return {"status": "partial_success", "warning": "Lost connection during commit, but deletion likely succeeded."}
        raise Exception(f"Database error during deletion: {str(e)}")

    except Exception as e:
        db.session.rollback()  # Rollback transaction on any unexpected error
        raise Exception(f"Failed to delete report: {str(e)}")


def get_folder_templates(folder_id):
    """Retrieve all templates for a specific folder without the file data."""
    try:
        # Check if the folder exists
        folder = execute_query('select', model=Folder,
                               filters={'id': folder_id})
        if not folder or len(folder) == 0:
            raise DatabaseError(f"Folder with ID {folder_id} not found")

        # Retrieve all templates associated with this folder, deferring the template_file field
        templates = db.session.query(Template).options(
            defer(Template.template_file)).filter_by(folder_id=folder_id).all()

        templates_list = []
        for template in templates:
            template_dict = template.to_dict()

            # Optionally, convert the template_image to Base64
            if template.template_image:
                encoded_image = base64.b64encode(
                    template.template_image).decode('utf-8')
                template_dict['template_image'] = f"data:image/png;base64,{encoded_image}"

            templates_list.append(template_dict)

        return {
            "folder_id": folder_id,
            "templates": templates_list
        }

    except SQLAlchemyError as e:
        raise DatabaseError(f"Database operation failed: {e}")
    except Exception as e:
        raise DatabaseError(f"An unexpected error occurred: {e}")


def get_file_of_report(report_id):
    """Retrieve the PPTX file data for a given report."""
    try:
        # Assuming 'Template' is the model that stores the report data
        report = execute_query('select', model=Template,
                               filters={'id': report_id})
        if not report or len(report) == 0:
            raise DatabaseError(f"Report with ID {report_id} not found")

        # Assuming report is a list and we want the first result
        report = report[0]

        if not report.template_file:
            raise DatabaseError(
                f"Report with ID {report_id} has no file associated with it")

        return report  # Return the binary data of the PPTX file

    except SQLAlchemyError as e:
        raise DatabaseError(f"Database operation failed: {e}")
    except Exception as e:
        raise DatabaseError(f"An unexpected error occurred: {e}")
