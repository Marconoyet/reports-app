from sqlalchemy.exc import SQLAlchemyError
from bson.objectid import ObjectId
from .custom_exceptions import DatabaseError
from models.folder_model import Folder
from db.db_utils import execute_query
from models.template_model import Template

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
        folder = execute_query('select', model=Folder, filters={'id': folder_id})

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
    """Update folder information by its ID."""
    try:
        result = current_app.db.folders.update_one(
            {"_id": ObjectId(folder_id)}, {"$set": updated_data})
        if result.matched_count == 0:
            raise DatabaseError(
                f"Folder with ID {folder_id} not found for update")
    except PyMongoError as e:
        raise DatabaseError(f"Failed to update folder: {e}")


def delete_folder_db(folder_id):
    """Delete a folder by its ID."""
    try:
        result = current_app.db.folders.delete_one(
            {"_id": ObjectId(folder_id)})
        if result.deleted_count == 0:
            raise DatabaseError(
                f"Folder with ID {folder_id} not found for deletion")
    except PyMongoError as e:
        raise DatabaseError(f"Failed to delete folder: {e}")


def add_file_to_folder_db(folder_id, file_metadata):
    """Add file metadata (report) to a folder in the MySQL database."""
    try:
        # Check if the folder exists
        folder = execute_query('select', model=Folder, filters={'id': folder_id})
        if not folder:
            raise DatabaseError(f"Folder with ID {folder_id} not found for update")

        # Add the report (file) to the templates table with folder_id as a foreign key
        file_metadata['folder_id'] = folder_id  # Link the file to the folder
        new_report_id = execute_query('insert', model=Template, data=file_metadata)
        
        return new_report_id  # Return the ID of the newly added report
    
    except SQLAlchemyError as e:
        raise DatabaseError(f"Database operation failed: {e}")
    
    except Exception as e:
        raise DatabaseError(f"An unexpected error occurred: {e}")



def list_folders_db():
    """Retrieve a list of all folders from the MySQL database using SQLAlchemy."""
    try:
        folders = execute_query('select', model=Folder)
        folder_list = []
        for folder in folders:
            folder_data = {
                'id': folder.id,
                'folder_name': folder.folder_name,
                'created_time': folder.created_time,
                'templates': folder.templates, 
            }
            folder_list.append(folder_data)
        return folder_list
    
    except SQLAlchemyError as e:
        raise Exception(f"Failed to list folders: {e}")