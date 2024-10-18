from db import db
from sqlalchemy.orm import joinedload, defer
from sqlalchemy import desc
from db.db_utils import execute_query
from datetime import datetime
from sqlalchemy.exc import SQLAlchemyError
from models.reports_model import Report
from .custom_exceptions import DatabaseError
from bson.objectid import ObjectId
from pymongo.errors import PyMongoError
from flask import current_app
from sqlmodel import SQLModel
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
        print(f"Error uploading report: {e}")
        raise Exception(f"Error uploading report: {e}")


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


def delete_file_db(file_id, folder_id):
    """Delete a file from the specified folder."""
    try:
        result = current_app.db.folders.update_one({"_id": ObjectId(folder_id)}, {
            "$pull": {"files": {"_id": ObjectId(file_id)}}})
        if result.matched_count == 0:
            raise DatabaseError(
                f"File with ID {file_id} not found in folder {folder_id}")
    except PyMongoError as e:
        raise DatabaseError(f"Failed to delete file: {e}")


def get_latest_reports(limit):
    """Retrieve the latest reports from the database."""
    try:
        # Use 'joinedload' to eagerly load the 'user' relationship
        latest_reports = (Report.query
                          .options(joinedload(Report.user))
                          .options(defer(Report.report_file))
                          .order_by(Report.created_time.desc())
                          .limit(limit)
                          .all())

        # Convert each report to a dictionary to send it to the frontend
        reports_list = [report.to_dict() for report in latest_reports]

        return reports_list

    except SQLAlchemyError as e:
        print(f"Database operation failed: {e}")
        raise Exception(f"Database operation failed: {e}")
