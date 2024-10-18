from flask import current_app
from pymongo.errors import PyMongoError
from .custom_exceptions import DatabaseError


def add_recent_open_db(recent_open_data):
    """Insert a new recent open record into Mongocurrent_app."""
    try:
        result = current_app.recent_open.insert_one(recent_open_data)
        return str(result.inserted_id)
    except PyMongoError as e:
        raise DatabaseError(f"Failed to add recent open: {e}")


def list_recent_open_db():
    """Retrieve a list of all recent open items."""
    try:
        return list(current_app.recent_open.find())
    except PyMongoError as e:
        raise DatabaseError(f"Failed to retrieve recent open data: {e}")


def clear_recent_open_db():
    """Clear the list of all recent open items."""
    try:
        result = current_app.recent_open.delete_many({})
        return result.deleted_count
    except PyMongoError as e:
        raise DatabaseError(f"Failed to clear recent open data: {e}")
