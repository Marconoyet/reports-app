from flask import current_app
from pymongo.errors import PyMongoError
from bson.objectid import ObjectId
from .custom_exceptions import DatabaseError
from models.template_model import Template
from sqlalchemy.exc import SQLAlchemyError
from db.db_utils import execute_query
from models.folder_model import Folder
from sqlalchemy.orm import defer
from db import db
import base64


def add_report_db(report_data):
    """Insert a new report into the MySQL database using SQLAlchemy."""
    try:
        new_report_id = execute_query('insert', model=Template, data=report_data)
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


def delete_report_db(report_id):
    """Delete a report by its ID."""
    try:
        result = current_app.db.reports.delete_one(
            {"_id": ObjectId(report_id)})
        if result.deleted_count == 0:
            raise DatabaseError(
                f"Report with ID {report_id} not found for deletion")
    except PyMongoError as e:
        raise DatabaseError(f"Failed to delete report: {e}")



def get_folder_templates(folder_id):
    """Retrieve all templates for a specific folder without the file data."""
    try:
        # Check if the folder exists
        folder = execute_query('select', model=Folder, filters={'id': folder_id})
        if not folder or len(folder) == 0:
            raise DatabaseError(f"Folder with ID {folder_id} not found")

        # Retrieve all templates associated with this folder, deferring the template_file field
        templates = db.session.query(Template).options(defer(Template.template_file)).filter_by(folder_id=folder_id).all()

        templates_list = []
        for template in templates:
            template_dict = template.to_dict()

            # Optionally, convert the template_image to Base64
            if template.template_image:
                encoded_image = base64.b64encode(template.template_image).decode('utf-8')
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
        report = execute_query('select', model=Template, filters={'id': report_id})
        if not report or len(report) == 0:
            raise DatabaseError(f"Report with ID {report_id} not found")
        
        report = report[0]  # Assuming report is a list and we want the first result
        
        if not report.template_file:
            raise DatabaseError(f"Report with ID {report_id} has no file associated with it")
        
        return report  # Return the binary data of the PPTX file

    except SQLAlchemyError as e:
        raise DatabaseError(f"Database operation failed: {e}")
    except Exception as e:
        raise DatabaseError(f"An unexpected error occurred: {e}")