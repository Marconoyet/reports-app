from sqlalchemy.orm import joinedload
from db import db
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import func
from models.users_model import User
from models.template_model import Template
from models.centers_model import Center
from models.reports_model import Report
from db.db_utils import execute_query
from db.custom_exceptions import DatabaseError
import base64


def create_center_db(center_data):
    try:
        logo_data = None
        if center_data.get('logo'):
            logo_data = base64.b64decode(center_data['logo'].split(',')[1])

        data = {
            "name": center_data.get('name'),
            "description": center_data.get('description'),
            "logo": logo_data,
            "color": center_data.get('color'),
            "country": center_data.get('country')
        }

        new_center_id = execute_query(action='insert', model=Center, data=data)

        for user_id in center_data.get('users', []):
            db.session.query(User).filter_by(
                id=user_id).update({"center_id": new_center_id})

        db.session.commit()
        return new_center_id

    except SQLAlchemyError as e:
        db.session.rollback()
        raise DatabaseError(f"Failed to create center and update users: {e}")


def get_center_db(center_id):
    try:
        center = db.session.query(Center).filter_by(id=center_id).first()
        if not center:
            raise DatabaseError(f"Center with ID {center_id} not found")
        return center.to_dict()
    except SQLAlchemyError as e:
        raise DatabaseError(f"Error retrieving center: {e}")


def update_center_db(center_id, updated_data):
    try:
        # Decode logo if it exists in updated_data
        if 'logo' in updated_data and updated_data['logo']:
            updated_data['logo'] = base64.b64decode(
                updated_data['logo'].split(',')[1]
            )

        # Update the Center data, ensuring there is data to update
        center_update_data = {key: updated_data[key]
                              for key in updated_data if key != 'users'}
        if center_update_data:  # Only update if there is data to update
            result = execute_query(
                action='update',
                model=Center,
                data=center_update_data,
                filters={'id': center_id}
            )

            if result == "No records found to update":
                raise DatabaseError(
                    f"Center with ID {center_id} not found for update")
        else:
            result = "No center data to update."

        # Update the center_id of users in the 'users' field
        if 'users' in updated_data:
            # Clear center_id from users not in the new list
            db.session.query(User).filter(User.center_id == center_id, User.id.notin_(
                updated_data['users'])).update({"center_id": None}, synchronize_session=False)

            # Set new center_id for the users in the updated list
            for user_id in updated_data['users']:
                db.session.query(User).filter_by(id=user_id).update(
                    {"center_id": center_id}, synchronize_session=False)

        db.session.commit()
        return result

    except SQLAlchemyError as e:
        db.session.rollback()
        raise DatabaseError(f"Failed to update center and assign users: {e}")


def delete_center_db(center_id):
    try:
        # Step 1: Delete all reports associated with the center
        execute_query(
            action='delete',
            model=Report,
            filters={'center_id': center_id}
        )

        # Step 2: Delete all templates associated with the center
        execute_query(
            action='delete',
            model=Template,
            filters={'center_id': center_id}
        )

        # Step 3: Update users associated with the center, but keep SuperAdmins
        db.session.query(User).filter(
            User.center_id == center_id, User.role != 'SuperAdmin'
        ).delete(synchronize_session=False)

        # Step 4: Set `center_id` to None for SuperAdmins in the specified center
        db.session.query(User).filter(
            User.center_id == center_id, User.role == 'SuperAdmin'
        ).update({"center_id": None}, synchronize_session=False)

        # Step 5: Delete the center itself
        result = execute_query(
            action='delete',
            model=Center,
            filters={'id': center_id}
        )

        # Commit the transaction
        db.session.commit()

        if result == "No records found to delete":
            raise DatabaseError(
                f"Center with ID {center_id} not found for deletion")

        return result
    except SQLAlchemyError as e:
        db.session.rollback()
        raise DatabaseError(
            f"Failed to delete center and associated data: {e}")
    except Exception as e:
        db.session.rollback()
        raise Exception(f"Unexpected error during deletion: {e}")


def list_centers_db():
    try:
        # Subquery to count distinct users per center
        user_count_subquery = (
            db.session.query(
                User.center_id,
                func.count(func.distinct(User.id)).label("user_count"),
                func.group_concat(func.distinct(User.id)).label("user_ids")
            )
            .group_by(User.center_id)
            .subquery()
        )

        # Subquery to count templates per center
        template_count_subquery = (
            db.session.query(
                Template.center_id,
                func.count(Template.id).label("template_count")
            )
            .group_by(Template.center_id)
            .subquery()
        )

        # Main query to retrieve centers and their counts
        centers = (
            db.session.query(
                Center,
                func.coalesce(user_count_subquery.c.user_count,
                              0).label("user_count"),
                func.coalesce(template_count_subquery.c.template_count, 0).label(
                    "template_count"),
                user_count_subquery.c.user_ids
            )
            .outerjoin(user_count_subquery, Center.id == user_count_subquery.c.center_id)
            .outerjoin(template_count_subquery, Center.id == template_count_subquery.c.center_id)
            .all()
        )

        centers_list = [
            {
                **center.Center.to_dict(),
                "user_count": center.user_count,
                "template_count": center.template_count,
                "user_ids": list(map(int, center.user_ids.split(','))) if center.user_ids else []
            }
            for center in centers
        ]

        return centers_list

    except SQLAlchemyError as e:
        raise DatabaseError(f"Failed to retrieve centers: {e}")


def get_center_admin_db(center_id):
    """Retrieve Super Admin, if not available retrieve an Admin for the specified center with deferred image loading."""
    try:
        # Query for a SuperAdmin first
        super_admin = db.session.query(User).options(
            db.defer(User.image)  # Defer loading of the image field
        ).filter_by(
            center_id=center_id, role='SuperAdmin'
        ).first()

        if super_admin:
            return super_admin.to_dict()  # Format the user data

        # If no SuperAdmin found, fallback to Admin
        admin = db.session.query(User).options(
            db.defer(User.image)  # Defer loading of the image field
        ).filter_by(
            center_id=center_id, role='Admin'
        ).first()

        if admin:
            return admin.to_dict()

        return None  # No SuperAdmin or Admin found

    except SQLAlchemyError as e:
        raise Exception(f"Failed to retrieve center admin: {e}")
