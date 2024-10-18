from db.users import (
    create_user_db,
    get_user_db,
    update_user_db,
    delete_user_db,
    list_users_db
)
from db.custom_exceptions import DatabaseError


def create_user(data):
    """Business logic for creating a user."""
    try:
        return create_user_db(data)
    except DatabaseError as e:
        raise Exception(f"Service Error - Could not create user: {e}")


def get_user(user_id):
    """Business logic for retrieving a user."""
    try:
        return get_user_db(user_id)
    except DatabaseError as e:
        raise Exception(f"Service Error - Could not retrieve user: {e}")


def update_user(user_id, data):
    """Business logic for updating a user."""
    try:
        return update_user_db(user_id, data)
    except DatabaseError as e:
        raise Exception(f"Service Error - Could not update user: {e}")


def delete_user(user_id):
    """Business logic for deleting a user."""
    try:
        return delete_user_db(user_id)
    except DatabaseError as e:
        raise Exception(f"Service Error - Could not delete user: {e}")


def list_users():
    """Business logic for listing all users."""
    try:
        return list_users_db()
    except DatabaseError as e:
        raise Exception(f"Service Error - Could not list users: {e}")
