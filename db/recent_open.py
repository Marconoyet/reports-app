from flask import current_app
from .custom_exceptions import DatabaseError
import json
from sqlalchemy.orm.exc import NoResultFound
from flask import current_app
from pymongo.errors import PyMongoError
from .custom_exceptions import DatabaseError
from models.template_model import Template
from sqlalchemy.orm import defer


from db.db_utils import execute_query
from models.users_model import User
from models.folder_model import Folder
from models.reports_model import Report
from models.template_model import Template

from db import db
import base64


def add_recent_open_db(recent_open_data):
    """
    Updates the clicked item for the user. Maintains a list of the last five clicked items
    for each category: folders, templates (reports), and generated reports.

    :param user_id: ID of the user
    :param item_type: Type of the item clicked ('folder', 'template', 'report')
    :param item_id: ID of the clicked item
    """
    try:
        user_id = recent_open_data.get("user_id")
        item_type = recent_open_data.get("item_type")
        item_id = recent_open_data.get("item_id")

        # Fetch user from the database
        user = db.session.query(User).filter_by(id=user_id).one()

        # Initialize clicked field as an empty dictionary if it doesn't exist
        clicked = json.loads(user.clicked) if user.clicked else {
            "folders": [], "templates": [], "reports": []
        }

        # Determine the correct category list to update
        if item_type == "folder":
            category = "folders"
        elif item_type == "template":
            category = "templates"
        elif item_type == "report":
            category = "reports"
        else:
            raise ValueError("Invalid item_type provided")

        # Update the clicked list for the category
        current_list = clicked[category]

        # Remove the item if it exists, then add it to the front
        if item_id in current_list:
            current_list.remove(item_id)
        current_list.insert(0, item_id)

        # Ensure that only the last 5 clicked items are kept
        if len(current_list) > 5:
            current_list = current_list[:5]

        # Update the category in the clicked dictionary
        clicked[category] = current_list

        # Save the updated clicked field in the user's record
        user.clicked = json.dumps(clicked)
        db.session.commit()
        print("User clicked item updated successfully.")

    except NoResultFound:
        raise Exception("User not found")
    except Exception as e:
        db.session.rollback()


def list_recent_open_db(user_id):
    try:
        # Fetch user from the database
        user = db.session.query(User).filter_by(id=user_id).one()

        # Parse the clicked items (folders, templates, reports)
        clicked = json.loads(user.clicked) if user.clicked else {
            "folders": [], "templates": [], "reports": []
        }

        # Fetch data from each table based on the clicked items,
        # while deferring loading of large fields (e.g., template_file)
        recent_folders = db.session.query(Folder).filter(
            Folder.id.in_(clicked["folders"])).all()

        recent_templates = db.session.query(Template).options(
            defer(Template.template_file)  # Defer loading large file
        ).filter(
            Template.id.in_(clicked["templates"])).all()

        # Fetch reports and join with the Template table to get the template image
        recent_reports = db.session.query(
            Report,
            Template.template_image  # Select the template image
        ).join(
            Template, Report.template_id == Template.id
        ).options(
            defer(Report.report_file)  # Defer loading large file
        ).filter(
            Report.id.in_(clicked["reports"])
        ).all()

        # Sort the fetched results based on the order in the clicked list
        recent_folders_dict = sorted(
            [folder.to_dict() for folder in recent_folders],
            key=lambda folder: clicked["folders"].index(folder["id"])
        )
        recent_templates_dict = sorted(
            [template.to_dict() for template in recent_templates],
            key=lambda template: clicked["templates"].index(template["id"])
        )
        recent_reports_dict = sorted(
            [
                {
                    **report.to_dict(),
                    "report_image": f"data:image/png;base64,{base64.b64encode(template_image).decode('utf-8')}" if template_image else None
                }
                for report, template_image in recent_reports
            ],
            key=lambda report: clicked["reports"].index(report["id"])
        )

        return {
            "recent_folders": recent_folders_dict,
            "recent_templates": recent_templates_dict,
            "recent_reports": recent_reports_dict
        }

    except NoResultFound:
        raise Exception("User not found")
    except Exception as e:
        raise Exception(f"Error fetching clicked items: {e}")



def clear_recent_open_db():
    """Clear the list of all recent open items."""
    try:
        result = current_app.recent_open.delete_many({})
        return result.deleted_count
    except PyMongoError as e:
        raise DatabaseError(f"Failed to clear recent open data: {e}")
