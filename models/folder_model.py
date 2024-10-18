from datetime import datetime
from flask import current_app
from db import db  # Import SQLAlchemy instanc
class Folder(db.Model):
    __tablename__ = 'folders'
    
    id = db.Column(db.Integer, primary_key=True)
    folder_name = db.Column(db.String(255), nullable=False)
    templates = db.Column(db.Text, nullable=True)  # JSON or text
    user_id = db.Column(db.Integer, nullable=False)  # Reference to the user who created it
    created_time = db.Column(db.DateTime, default=datetime.utcnow)
    

    def __init__(self, folder_name, templates, user_id):
        self.folder_name = folder_name
        self.templates = templates
        self.user_id = user_id

    def to_dict(self):
        return {
            "id": self.id,
            "folder_name": self.folder_name,
            "created_time": self.created_time.isoformat().replace("T", " "), 
        }
