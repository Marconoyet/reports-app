from sqlalchemy import Column, BigInteger, String, Text, LargeBinary, DateTime, ForeignKey, create_engine
from db import db
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
from models.centers_model import Center

import base64


class Template(db.Model):
    __tablename__ = 'templates'  # The name of the table in your database
    __table_args__ = {'schema': 'u704613426_reports'}
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    template_name = Column(String(255), nullable=False)  # Name of the template
    template_description = Column(Text, nullable=True)
    template_image = Column(LargeBinary, nullable=True)
    template_file = Column(LargeBinary, nullable=True)
    user_id = Column(BigInteger, ForeignKey("u704613426_reports.users.id"),
                     nullable=False)  # Foreign key referencing the users table
    folder_id = Column(BigInteger, ForeignKey("folders.id"), nullable=False)
    created_time = Column(DateTime, default=datetime.utcnow)
    center_id = db.Column(db.Integer, db.ForeignKey(Center.id))

    def __repr__(self):
        return f"<Template(id={self.id}, name={self.template_name})>"

    def to_dict(self):
        return {
            "id": self.id,
            "template_name": self.template_name,
            "template_image": f"data:image/png;base64,{base64.b64encode(self.template_image).decode('utf-8')}" if self.template_image else None,
            "template_description": self.template_description,
            "folder_id": self.folder_id,
            "user_id": self.user_id,
            "center_id": self.center_id,
            "created_time": self.created_time.isoformat().replace("T", " "),
        }
