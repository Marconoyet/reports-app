from flask import current_app
from flask import jsonify
import bcrypt
from pymongo.errors import PyMongoError
from bson.objectid import ObjectId
from .custom_exceptions import DatabaseError
from models.users_model import User
from sqlalchemy.exc import SQLAlchemyError
from db import db
from models.users_model import User  # Assuming your User model is in models.py
from db.db_utils import execute_query
import base64
import hashlib
PBKDF2_ITERATIONS=10000
STATIC_SALT = "6876513b9ea1ad4ddbd47dd43a1f36903ae6930cd7c8d33368011227031a242e"
def create_user_db(user_data):
    """Insert a new user into the SQL database using the execute_query function."""
    try:
        # Prepare the data dictionary for the new user
        image_data = None
        if user_data.get('image'):
            image_data = base64.b64decode(user_data['image'].split(',')[1])
        data = {
            "first_name": user_data.get('firstName'),
            "last_name": user_data.get('lastName'),
            "email": user_data.get('email'),
            "username": user_data.get('username'),
            "password": user_data.get('password'),  # Ensure password is hashed
            "role": user_data.get('role'),
            "position": user_data.get('position'),
            "image": image_data,
            "deactivated": user_data.get('deactivated', False),  # Default to False
            "deleted": user_data.get('deleted', False)  # Default to False
        }

        # Use the execute_query function to insert the new user
        new_user_id = execute_query(action='insert', model=User, data=data)
        
        # Return the ID of the newly created user
        return new_user_id

    except SQLAlchemyError as e:
        db.session.rollback()
        raise Exception(f"Failed to create user: {e}")



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
    """Update a user's information by their ID using execute_query."""
    try:
        # Decode the image if it's present
        if 'image' in updated_data and updated_data['image']:
            image_data = base64.b64decode(updated_data['image'].split(',')[1])
            updated_data['image'] = image_data  # Use dictionary syntax to update
        
        # Use execute_query with the 'update' action
        result = execute_query(
            action='update',
            model=User,
            data=updated_data,
            filters={'id': user_id}
        )
        
        if result == "No records found to update":
            raise DatabaseError(f"User with ID {user_id} not found for update")

        return result
    except SQLAlchemyError as e:
        raise DatabaseError(f"Failed to update user: {e}")



def delete_user_db(user_id):
    """Delete a user by their ID using execute_query."""
    try:
        # Use execute_query with the 'delete' action
        result = execute_query(
            action='delete',
            model=User,
            filters={'id': user_id}
        )
        
        if result == "No records found to delete":
            raise DatabaseError(f"User with ID {user_id} not found for deletion")
        
        return result
    except SQLAlchemyError as e:
        raise DatabaseError(f"Failed to delete user: {e}")


def list_users_db():
    """Retrieve all users from the database using execute_query."""
    try:
        users = execute_query('select', model=User)
        users_list = [user.to_dict() for user in users]
        return users_list
    except Exception as e:
        raise Exception(f"Failed to retrieve users: {e}")

def check_email_db(email):
    try:
        user = db.session.query(User).filter_by(email=email).first()
        return user
    except SQLAlchemyError as e:
        raise Exception(f"Failed to check user email: {e}")

def check_username_db(username):
    try:
        user = db.session.query(User).filter_by(username=username).first()
        return user
    except SQLAlchemyError as e:
        raise Exception(f"Failed to check user username: {e}")


def hash_password_with_salt(password):
    # Derive the key using PBKDF2 with HMAC-SHA256
    dk = hashlib.pbkdf2_hmac(
        hash_name='sha256',
        password=password.encode('utf-8'),  # Password needs to be in bytes
        salt=STATIC_SALT.encode('utf-8'),  # Salt needs to be in bytes
        iterations=PBKDF2_ITERATIONS,
        dklen=32  # Output key length in bytes (256 bits)
    )
    # Convert the derived key to a hexadecimal string
    return dk.hex()

def check_user_credentials(username_or_email, client_hashed_password):
    try:
        # Retrieve the user from the database by username or email
        user = db.session.query(User.id, User.username, User.email, User.password, User.role, User.first_login)\
                         .filter(
                             (User.email == username_or_email) | (User.username == username_or_email)
                         ).first()
        
        # If no user is found with the provided username or email
        if not user:
            return {"success": False, "message": "The Username or Password is Incorrect. Try again."}
        
        # If the user exists, compare the hashed password
        server_hashed_password = user.password
        # print(server_hashed_password)
        # print(client_hashed_password)
        if server_hashed_password == client_hashed_password:
            # Password is correct
            return {
                "success": True,
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                    "firstLogin": user.first_login,
                    "role": user.role
                }
            }
        else:
            # If the password is incorrect
            return {"success": False, "message": "The Username or Password is Incorrect. Try again."}
    except SQLAlchemyError as e:
        raise Exception(f"Failed to check user credentials: {e}")
