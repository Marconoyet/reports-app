from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from config import Config  # Import the configuration class
# Create a MetaData object with a default schema

default_metadata = MetaData(schema='u704613426_reports')
db = SQLAlchemy(metadata=default_metadata)
def init_db(app):
    try:

        app.config.from_object(Config)
        db.init_app(app)
        with app.app_context():
            db.create_all()
        print("Database connected successfully.")
        
    except Exception as e:
        print(f"Error connecting to database: {e}")
