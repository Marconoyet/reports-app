from sqlalchemy.exc import SQLAlchemyError, OperationalError
from sqlalchemy import desc
from flask import current_app
from db import db


def execute_query(action, model=None, data=None, filters=None, limit=None):
    """General function to connect to the database and execute queries."""
    try:
        with current_app.app_context():
            if action == 'select':
                # Handle the case where filters may be None or empty
                if filters is None:
                    filters = {}
                result = model.query.filter_by(**filters).all()
                return result

            elif action == 'select_with_limit':
                # Fetch records with optional filters and a limit
                if filters is None:
                    filters = {}
                result = model.query.filter_by(
                    **filters).order_by(desc(model.created_time)).limit(limit).all()
                return result

            elif action == 'insert':
                new_record = model(**data)
                db.session.add(new_record)
                db.session.commit()
                return new_record.id

            elif action == 'update':
                records = model.query.filter_by(**filters)
                if records:
                    records.update(data)
                    db.session.commit()
                    return f"{records.count()} record(s) updated"
                else:
                    return "No records found to update"

            elif action == 'delete':
                records = model.query.filter_by(**filters)
                count = records.count()
                if count > 0:
                    records.delete()
                    db.session.commit()
                    return f"{count} record(s) deleted"
                else:
                    return "No records found to delete"

    except OperationalError as oe:
        db.session.rollback()
        raise Exception(
            f"Database operation failed: MySQL Connection not available. {oe}")

    except SQLAlchemyError as e:
        db.session.rollback()
        raise Exception(f"Database operation failed: {e}")
