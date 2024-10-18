from db.folders import (
    create_folder_db,
    get_folder_db,
    update_folder_db,
    delete_folder_db,
    list_folders_db
)
from db.reports import get_folder_templates
from db.custom_exceptions import DatabaseError


def create_folder(data):
    """Business logic for creating a folder."""
    try:
        return create_folder_db(data)
    except DatabaseError as e:
        raise Exception(f"Service Error - Could not create folder: {e}")


def get_folder(folder_id):
    """Business logic for retrieving a folder and its associated templates."""
    try:
        # Retrieve folder data
        folder_data = get_folder_db(folder_id)
        
        # Retrieve templates associated with the folder
        folder_templates_data = get_folder_templates(folder_id)

        # Combine folder data and templates into a single dictionary
        combined_data = {
            "folder": folder_data,            # Folder details
            "templates": folder_templates_data['templates']  # Templates associated with the folder
        }


        return combined_data
    
    except DatabaseError as e:
        raise Exception(f"Service Error - Could not retrieve folder: {e}")



def update_folder(folder_id, data):
    """Business logic for updating a folder."""
    try:
        return update_folder_db(folder_id, data)
    except DatabaseError as e:
        raise Exception(f"Service Error - Could not update folder: {e}")


def delete_folder(folder_id):
    """Business logic for deleting a folder."""
    try:
        return delete_folder_db(folder_id)
    except DatabaseError as e:
        raise Exception(f"Service Error - Could not delete folder: {e}")


def list_folders():
    """Business logic for listing all folders."""
    try:
        return list_folders_db()
    except DatabaseError as e:
        raise Exception(f"Service Error - Could not list folders: {e}")
