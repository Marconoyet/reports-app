from db.users import (
    create_user_db,
    get_user_db,
    update_user_db,
    delete_user_db,
    list_users_db,
    check_email_db,
    check_username_db,
    check_user_credentials
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

def check_users_email(email):
    """Business logic for check users email"""
    try:
        return check_email_db(email)
    except DatabaseError as e:
        raise Exception(f"Service Error - Could not list users: {e}")

def check_users_username(username):
    """Business logic for check users username"""
    try:
        return check_username_db(username)
    except DatabaseError as e:
        raise Exception(f"Service Error - Could not list users: {e}")
def check_users_login(username_or_email, password):
    """Business logic for check users login"""
    try:
        return check_user_credentials(username_or_email, password)
    except DatabaseError as e:
        raise Exception(f"Service Error - Could not list users: {e}")
