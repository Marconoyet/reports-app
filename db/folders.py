from sqlalchemy import func
from sqlalchemy.exc import SQLAlchemyError
from bson.objectid import ObjectId
from .custom_exceptions import DatabaseError
from models.folder_model import Folder
from db.db_utils import execute_query
from models.template_model import Template
from db import db


def create_folder_db(folder_data):
    """Insert a new folder into the MySQL database using SQLAlchemy."""
    try:
        print(folder_data)
        new_folder_id = execute_query('insert', model=Folder, data=folder_data)
        return new_folder_id
    except SQLAlchemyError as e:
        raise DatabaseError(f"An unexpected error occurred: {e}")


def get_folder_db(folder_id):
    """Retrieve a folder by its ID from the MySQL database using SQLAlchemy."""
    try:
        # Use the execute_query function to retrieve the folder based on folder_id
        folder = execute_query('select', model=Folder,
                               filters={'id': folder_id})

        if not folder or len(folder) == 0:
            raise DatabaseError(f"Folder with ID {folder_id} not found")

        # Assuming only one folder is returned, take the first item from the result
        folder = folder[0]  # Since execute_query returns a list of results

        # Convert the Folder object to a dictionary using the to_dict() method
        return folder.to_dict()

    except SQLAlchemyError as e:
        raise DatabaseError(f"Database operation failed: {e}")
    except Exception as e:
        raise DatabaseError(f"An unexpected error occurred: {e}")


def update_folder_db(folder_id, updated_data):
    """
    Update folder information by its ID in the SQL database using execute_query.

    :param folder_id: The ID of the folder to update.
    :param updated_data: A dictionary containing the fields to update.
    :raises: Exception if the update fails or the folder is not found.
    """
    try:
        # The filters argument is used to find the correct folder by id
        filters = {"id": folder_id}

        # Execute the update query using execute_query
        result = execute_query('update', model=Folder,
                               data=updated_data, filters=filters)

        return result

    except Exception as e:
        raise Exception(f"Failed to update folder: {e}")


def delete_folder_db(folder_id):
    """
    Delete a folder by its ID and delete all associated templates.

    :param folder_id: The ID of the folder to delete.
    """
    try:
        # Step 1: Delete all templates associated with this folder
        execute_query(
            action='delete',
            model=Template,
            filters={'folder_id': folder_id}
        )

        # Step 2: Delete the folder itself
        result = execute_query(
            action='delete',
            model=Folder,
            filters={'id': folder_id}
        )

        if result == "No records found to delete":
            raise Exception(
                f"Folder with ID {folder_id} not found for deletion")

        return f"Folder and associated templates deleted successfully."

    except SQLAlchemyError as e:
        db.session.rollback()
        raise Exception(
            f"Failed to delete folder and associated templates: {e}")


def add_file_to_folder_db(folder_id, file_metadata):
    """Add file metadata (report) to a folder in the MySQL database."""
    try:
        # Check if the folder exists
        folder = execute_query('select', model=Folder,
                               filters={'id': folder_id})
        if not folder:
            raise DatabaseError(
                f"Folder with ID {folder_id} not found for update")

        # Add the report (file) to the templates table with folder_id as a foreign key
        file_metadata['folder_id'] = folder_id  # Link the file to the folder
        new_report_id = execute_query(
            'insert', model=Template, data=file_metadata)

        return new_report_id  # Return the ID of the newly added report

    except SQLAlchemyError as e:
        raise DatabaseError(f"Database operation failed: {e}")

    except Exception as e:
        raise DatabaseError(f"An unexpected error occurred: {e}")


def list_folders_db():
    """Retrieve a list of all folders with the number of templates in each folder."""
    try:
        # Perform a query that joins Folder and Template and counts the number of templates per folder
        folders_with_template_count = db.session.query(
            Folder.id,
            Folder.folder_name,
            Folder.created_time,
            func.count(Template.id).label('template_count')
        ).outerjoin(Template, Folder.id == Template.folder_id).group_by(Folder.id).all()

        folder_list = []
        for folder in folders_with_template_count:
            folder_data = {
                'id': folder.id,
                'folder_name': folder.folder_name,
                'created_time': folder.created_time,
                'template_count': folder.template_count  # Count of templates in this folder
            }
            folder_list.append(folder_data)

        return folder_list

    except SQLAlchemyError as e:
        raise Exception(f"Failed to list folders: {e}")
