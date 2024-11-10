from db.centers import (
    create_center_db,
    get_center_db,
    update_center_db,
    delete_center_db,
    list_centers_db
)

from db.custom_exceptions import DatabaseError


def create_center(data):
    try:
        return create_center_db(data)
    except DatabaseError as e:
        raise Exception(f"Service Error - Could not create center: {e}")


def get_center(center_id):
    try:
        return get_center_db(center_id)
    except DatabaseError as e:
        raise Exception(f"Service Error - Could not retrieve center: {e}")


def update_center(center_id, data):
    try:
        return update_center_db(center_id, data)
    except DatabaseError as e:
        raise Exception(f"Service Error - Could not update center: {e}")


def delete_center(center_id):
    try:
        return delete_center_db(center_id)
    except DatabaseError as e:
        raise Exception(f"Service Error - Could not delete center: {e}")


def list_centers():
    try:
        return list_centers_db()
    except DatabaseError as e:
        raise Exception(f"Service Error - Could not list centers: {e}")

def fetch_user_and_center(user_id):
    from services.users_service import get_user
    try:
        # Retrieve user data
        user = get_user(user_id)
        if not user:
            return None, None, "User not found"

        # Retrieve center data if it exists for the user
        center = None
        if user.get("center_id"):
            center = get_center_db(user["center_id"])

        return user, center, None
    except Exception as e:
        return None, None, str(e)