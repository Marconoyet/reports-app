from flask import current_app
from flask import jsonify
import bcrypt
from pymongo.errors import PyMongoError
from bson.objectid import ObjectId
from .custom_exceptions import DatabaseError
from models.users_model import User
from models.centers_model import Center
from db.centers import get_center_db
from services.centers_service import get_center
from sqlalchemy.exc import SQLAlchemyError
from db import db
from db.db_utils import execute_query
import base64
import hashlib

PBKDF2_ITERATIONS = 10000
STATIC_SALT = "6876513b9ea1ad4ddbd47dd43a1f36903ae6930cd7c8d33368011227031a242e"


def create_user_db(user_data, center_id):
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
            "center_id": center_id,
            "deactivated": user_data.get('deactivated', False),
            "deleted": user_data.get('deleted', False)  # Default to False
        }

        # Retrieve center data
        center_data = get_center_db(center_id)

        # Use the execute_query function to insert the new user
        new_user_id = execute_query(action='insert', model=User, data=data)
        data["id"] = new_user_id

        # Return the user data with the associated center data as an embedded object
        return {
            **data,
            "center": center_data if center_data else None  # Assuming center_data has a to_dict method
        }

    except SQLAlchemyError as e:
        db.session.rollback()
        raise Exception(f"Failed to create user: {e}")



def get_user_db(user_id):
    """Retrieve a user by their ID from the SQL database."""
    try:
        user = db.session.query(User).filter_by(id=user_id).first()
        if not user:
            raise DatabaseError(f"User with ID {user_id} not found")
        return user.to_dict()  # Assuming the User model has a to_dict method
    except SQLAlchemyError as e:
        raise DatabaseError(f"Error retrieving user: {e}")
    except Exception as e:
        raise DatabaseError(f"An unexpected error occurred: {e}")
    
def get_user_db_basic(user_id):
    """Retrieve a user by their ID from the SQL database, excluding image data."""
    try:
        # Query the user but exclude the image field for faster response times
        user = db.session.query(
            User.id,
            User.role,
            User.center_id,
        ).filter_by(id=user_id).first()

        if not user:
            raise DatabaseError(f"User with ID {user_id} not found")

        # Convert query result to a dictionary
        user_dict = {
            "id": user.id,
            "role": user.role,
            "center_id": user.center_id,
        }

        return user_dict
    except SQLAlchemyError as e:
        raise DatabaseError(f"Error retrieving user: {e}")
    except Exception as e:
        raise DatabaseError(f"An unexpected error occurred: {e}")
    


def update_user_db(user_id, updated_data):
    """Update a user's information by their ID using execute_query."""
    try:
        # Decode the image if it's present
        if 'image' in updated_data and updated_data['image']:
            image_data = base64.b64decode(updated_data['image'].split(',')[1])
            # Use dictionary syntax to update
            updated_data['image'] = image_data

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
            raise DatabaseError(
                f"User with ID {user_id} not found for deletion")

        return result
    except SQLAlchemyError as e:
        raise DatabaseError(f"Failed to delete user: {e}")


def list_users_db(center_id=None):
    """Retrieve users along with their associated center details."""
    try:
        # Base query to fetch users and their associated centers
        query = db.session.query(User, Center).outerjoin(Center, User.center_id == Center.id)
        
        # Apply filter if center_id is provided
        if center_id is not None:
            query = query.filter(User.center_id == center_id)
        
        # Execute the query
        users_with_centers = query.all()

        # Format the response to include users and their center details
        users_list = [
            {
                **user.to_dict(),
                "image": f"data:image/png;base64,{base64.b64encode(user.image).decode('utf-8')}" if user.image else None,
                "center": {
                    "id": center.id if center else None,
                    "name": center.name if center else None,
                    "description": center.description if center else None,
                    "img": f"data:image/png;base64,{base64.b64encode(center.logo).decode('utf-8')}" if center and center.logo else None,
                    "color": center.color if center else None,
                    "country": center.country if center else None,
                    "created_at": center.created_at.isoformat() if center and center.created_at else None,
                } if center else None  # Center details only if a center exists
            }
            for user, center in users_with_centers
        ]

        return users_list

    except SQLAlchemyError as e:
        raise DatabaseError(f"Failed to retrieve users with center details: {e}")



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
        user = db.session.query(User).filter(
            (User.email == username_or_email) | (User.username == username_or_email)
        ).first()

        # If no user is found with the provided username or email
        if not user:
            return {"success": False, "message": "The Username or Password is Incorrect. Try again."}

        # Compare the hashed password
        server_hashed_password = user.password
        if server_hashed_password == client_hashed_password:
            # Retrieve center data if the user has a center_id
            center = None
            if user.center_id:
                center = get_center_db(user.center_id)  # Retrieve center using the provided function

            # Use the model's to_dict method for JSON serialization
            return {
                "success": True,
                "user": user.to_dict(),
                "center": center if center else None  # Convert center to dict if it exists
            }
        else:
            # If the password is incorrect
            return {"success": False, "message": "The Username or Password is Incorrect. Try again."}

    except SQLAlchemyError as e:
        raise Exception(f"Failed to check user credentials: {e}")

