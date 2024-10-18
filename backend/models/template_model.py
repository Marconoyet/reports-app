from sqlalchemy import Column, BigInteger, String, Text, LargeBinary, DateTime, ForeignKey, create_engine
from db import db
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

class Template(db.Model):
    __tablename__ = 'templates'  # The name of the table in your database
    __table_args__= {'schema':'u704613426_reports'}
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    template_name = Column(String(255), nullable=False)  # Name of the template
    template_description = Column(Text, nullable=True)  # Description of the template
    template_image = Column(LargeBinary, nullable=True)  # Image of the template
    template_file = Column(LargeBinary, nullable=True)  # File associated with the template
    user_id = Column(BigInteger, ForeignKey("u704613426_reports.users.id"), nullable=False)  # Foreign key referencing the users table
    folder_id = Column(BigInteger, ForeignKey("folders.id"), nullable=False)  # Foreign key referencing the users table
    created_time = Column(DateTime, default=datetime.utcnow)  # Timestamp for when the template is created

    def __repr__(self):
        return f"<Template(id={self.id}, name={self.template_name})>"
    def to_dict(self):
        return {
            "id": self.id,
            "template_name": self.template_name,
            "template_description": self.template_description,
            "folder_id": self.folder_id,
            "user_id": self.user_id,
            "created_time": self.created_time.isoformat().replace("T", " "), 
        }