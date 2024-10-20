from db.recent_open import (
    add_recent_open_db,
    list_recent_open_db,
    clear_recent_open_db
)
from db.custom_exceptions import DatabaseError


def add_recent_open(recent_open_data):
    """Business logic for adding a recent open entry."""
    try:
        return add_recent_open_db(recent_open_data)
    except DatabaseError as e:
        raise Exception(
            f"Service Error - Could not add recent open entry: {e}")


def list_recent_open(user_id):
    """Business logic for listing all recent open entries."""
    try:
        return list_recent_open_db(user_id)
    except DatabaseError as e:
        raise Exception(
            f"Service Error - Could not list recent open entries: {e}")


def clear_recent_open():
    """Business logic for clearing recent open entries."""
    try:
        return clear_recent_open_db()
    except DatabaseError as e:
        raise Exception(
            f"Service Error - Could not clear recent open entries: {e}")
