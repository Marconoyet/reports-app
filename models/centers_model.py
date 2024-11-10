from datetime import datetime
from flask import current_app
from db import db  # Import SQLAlchemy instance
import base64


class Center(db.Model):
    __tablename__ = 'centers'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=True)
    logo = db.Column(db.LargeBinary, nullable=True)
    color = db.Column(db.String(10), nullable=True)  # Hex color code
    country = db.Column(db.String(5), nullable=True)  # Country code
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __init__(self, name, description=None, logo=None, color=None, country=None):
        self.name = name
        self.description = description
        self.logo = logo
        self.color = color
        self.country = country

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "color": self.color,
            "country": self.country,
            "created_at": self.created_at.isoformat().replace("T", " "),
            "logo": f"data:image/png;base64,{base64.b64encode(self.logo).decode('utf-8')}" if self.logo else None,
        }
