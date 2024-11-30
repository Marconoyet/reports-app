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
    """Retrieve paginated reports from the database along with their centers and template details."""
    try:
        # Step 1: Base query for reports with pagination and optional center filtering
        query = Report.query.options(
            joinedload(Report.user), 
            joinedload(Report.template).defer(Template.template_file)  # Join template and avoid loading large file
        )

        # Apply filtering by center_id if provided
        if center_id is not None:
            query = query.filter(Report.center_id == center_id)

        # Count total records for pagination
        total_records = query.count()

        # Apply limit and offset for pagination
        paginated_reports = (
            query.order_by(Report.created_time.desc())
            .limit(limit)
            .offset((page - 1) * limit)
            .all()
        )

        # Step 2: Get unique center IDs and template IDs from the reports
        center_ids = {report.center_id for report in paginated_reports if report.center_id}
        template_ids = {report.template_id for report in paginated_reports if report.template_id}

        # Step 3: Query centers and templates once for all unique IDs
        centers = {}
        templates = {}
        
        if center_ids:
            center_records = Center.query.filter(Center.id.in_(center_ids)).all()
            centers = {center.id: center.to_dict() for center in center_records}

        if template_ids:
            template_records = Template.query.filter(Template.id.in_(template_ids)).all()
            templates = {
                template.id: {
                    **template.to_dict(),
                    "template_image": f"data:image/png;base64,{base64.b64encode(template.template_image).decode('utf-8')}" if template.template_image else None
                }
                for template in template_records
            }

        # Step 4: Convert reports to list of dicts and attach center and template data
        reports_list = [
            {
                **report.to_dict(),
                "center": centers.get(report.center_id),  # Attach center data if available
                "template": templates.get(report.template_id),  # Attach template data if available
            }
            for report in paginated_reports
        ]

        return reports_list, total_records
    except SQLAlchemyError as e:
        print(f"Database operation failed: {e}")
        raise Exception(f"Database operation failed: {e}")
