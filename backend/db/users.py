from flask import current_app

from pymongo.errors import PyMongoError
from bson.objectid import ObjectId
from .custom_exceptions import DatabaseError


def create_user_db(user_data):
    """Insert a new user into the Mongocurrent_app.db."""
    try:
        result = current_app.db.users.insert_one(user_data)
        return str(result.inserted_id)
    except PyMongoError as e:
        raise DatabaseError(f"Failed to create user: {e}")


def get_user_db(user_id):
    """Retrieve a user by their ID."""
    try:
        user = current_app.db.users.find_one({"_id": ObjectId(user_id)})
        if not user:
            raise DatabaseError(f"User with ID {user_id} not found")
        return user
    except PyMongoError as e:
        raise DatabaseError(f"Error retrieving user: {e}")
    except Exception as e:
        raise DatabaseError(f"An unexpected error occurred: {e}")


def update_user_db(user_id, updated_data):
    """Update a user's information by their ID."""
    try:
        result = current_app.db.users.update_one(
            {"_id": ObjectId(user_id)}, {"$set": updated_data})
        if result.matched_count == 0:
            raise DatabaseError(f"User with ID {user_id} not found for update")
    except PyMongoError as e:
        raise DatabaseError(f"Failed to update user: {e}")


def delete_user_db(user_id):
    """Delete a user by their ID."""
    try:
        result = current_app.db.users.delete_one({"_id": ObjectId(user_id)})
        if result.deleted_count == 0:
            raise DatabaseError(
                f"User with ID {user_id} not found for deletion")
    except PyMongoError as e:
        raise DatabaseError(f"Failed to delete user: {e}")


def list_users_db():
    """Retrieve a list of all users."""
    try:
        return list(current_app.db.users.find())
    except PyMongoError as e:
        raise DatabaseError(f"Failed to list users: {e}")
