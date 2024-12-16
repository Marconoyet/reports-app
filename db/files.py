from db import db
from sqlalchemy.orm import joinedload, defer
from sqlalchemy import desc
from db.db_utils import execute_query
from datetime import datetime
from sqlalchemy.exc import SQLAlchemyError
from models.reports_model import Report
from models.centers_model import Center
from models.template_model import Template
from .custom_exceptions import DatabaseError
from bson.objectid import ObjectId
from pymongo.errors import PyMongoError
from flask import current_app
from sqlmodel import SQLModel
import base64
SQLModel.metadata.schema = "u704613426_reports"


def get_file_db(report_id):
    """Upload a new report file to the database."""
    try:
        # Insert the new report into the database using execute_query
        report = execute_query('select', model=Report,
                               filters={'id': report_id})
        return report[0]
    except SQLAlchemyError as e:
        print(f"Database operation failed: {e}")
        raise Exception(f"Database operation failed: {e}")
    except Exception as e:
        print(f"Error getting report: {e}")
        raise Exception(f"Error getting report: {e}")


def get_report_with_template_data(report_id):
    """
    Fetch report data and map it to the template structure.
    """
    try:
        # Create a session
        session = db.session

        # Fetch the report from the database and rebind to session
        report = session.query(Report).filter_by(id=report_id).first()
        if not report:
            raise Exception(f"Report with ID {report_id} not found.")

        # Decode the report file
        file_data = report.report_file
        html_file_content = file_data.decode('utf-8') if file_data else None

        # Convert report data to a dictionary
        report_data = report.to_dict()

        # Fetch the associated template
        template = session.query(Template).filter_by(
            id=report.template_id).first()
        if not template:
            raise Exception(
                f"Template with ID {report.template_id} not found.")

        # Process the template image (convert binary to Base64)
        template_image_base64 = None
        if template.template_image:
            template_image_base64 = base64.b64encode(
                template.template_image).decode('utf-8')

        # Map the data to the desired structure
        mapped_data = {
            "template_name": report_data.get("report_name"),
            "template_file": html_file_content,
            "created_time": report_data.get("created_time"),
            "template_description": template.template_description,
            "template_image": f"data:image/png;base64,{template_image_base64}" if template_image_base64 else None,
        }

        return mapped_data

    except SQLAlchemyError as e:
        print(f"Database operation failed: {e}")
        raise Exception(f"Database operation failed: {e}")
    except Exception as e:
        print(f"Error mapping report and template data: {e}")
        raise Exception(f"Error mapping report and template data: {e}")


def update_file_db(report_id, updated_data):
    """Update report information by its ID."""
    try:
        filters = {'id': report_id}
        result = execute_query('update', model=Report,
                               data=updated_data, filters=filters)
        if result == "No records found to update":
            raise Exception(f"Report with ID {report_id} not found for update")
        return result

    except Exception as e:
        raise Exception(f"Failed to update report: {e}")


def upload_file_db(report_data):
    """Upload a new report file to the database."""
    try:
        # Insert the new report into the database using execute_query
        report_id = execute_query('insert', model=Report, data=report_data)
        return {"status": "success", "report_id": report_id}

    except SQLAlchemyError as e:
        print(f"Database operation failed: {e}")
        raise Exception(f"Database operation failed: {e}")
    except Exception as e:
        print(f"Error uploading report: {e}")
        raise Exception(f"Error uploading report: {e}")


def move_file_db(file_id, from_folder, to_folder):
    """Move a file from one folder to another."""
    try:
        file = current_app.db.folders.find_one({"_id": ObjectId(
            from_folder), "files._id": ObjectId(file_id)}, {"files.$": 1})['files'][0]
        if not file:
            raise DatabaseError(
                f"File with ID {file_id} not found in folder {from_folder}")
        current_app.db.folders.update_one({"_id": ObjectId(to_folder)}, {
            "$push": {"files": file}})
        current_app.db.folders.update_one({"_id": ObjectId(from_folder)}, {
            "$pull": {"files": {"_id": ObjectId(file_id)}}})
    except PyMongoError as e:
        raise DatabaseError(f"Failed to move file: {e}")
    except Exception as e:
        raise DatabaseError(f"An unexpected error occurred: {e}")


def delete_file_db(file_id):
    """Delete a file from the database using MySQL."""
    try:
        file_to_delete = db.session.query(Report).filter_by(id=file_id).first()
        if not file_to_delete:
            raise DatabaseError(f"File with ID {file_id} not found")
        # Delete the file
        db.session.delete(file_to_delete)
        db.session.commit()
        return {"status": "success", "message": f"File with ID {file_id} deleted successfully"}
    except SQLAlchemyError as e:
        db.session.rollback()
        raise DatabaseError(f"Failed to delete file: {e}")


def get_latest_reports(limit, page, center_id=None):
    """Retrieve paginated reports from the database with optimized performance."""
    try:
        # Step 1: Query paginated reports and preload necessary relationships
        query = (
            Report.query.options(
                joinedload(Report.user),  # Preload user relationship
                # Preload template but defer large file
                joinedload(Report.template).defer(Template.template_file)
            )
            .order_by(Report.created_time.desc())
        )

        # Apply center_id filtering if provided
        if center_id is not None:
            query = query.filter(Report.center_id == center_id)

        # Fetch paginated reports with limit and offset
        total_records = query.count()
        paginated_reports = query.limit(limit).offset((page - 1) * limit).all()

        # Use bulk loading to reduce queries
        center_ids = {
            report.center_id for report in paginated_reports if report.center_id}
        template_ids = {
            report.template_id for report in paginated_reports if report.template_id}

        centers = {
            center.id: center.to_dict()
            for center in Center.query.filter(Center.id.in_(center_ids))
        } if center_ids else {}

        templates = {
            template.id: {
                **template.to_dict(),
                "template_image": f"data:image/png;base64,{base64.b64encode(template.template_image).decode('utf-8')}" if template.template_image else None,
            }
            for template in Template.query.filter(Template.id.in_(template_ids))
        } if template_ids else {}

        # Combine report data with preloaded center and template data
        reports_list = [
            {
                **report.to_dict(),
                "center": centers.get(report.center_id),
                "template": templates.get(report.template_id),
            }
            for report in paginated_reports
        ]

        return reports_list, total_records
    except SQLAlchemyError as e:
        print(f"Database operation failed: {e}")
        raise Exception(f"Database operation failed: {e}")
