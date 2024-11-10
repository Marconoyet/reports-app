from sqlalchemy import Column, BigInteger, String, DateTime, Boolean, Text, LargeBinary
from datetime import datetime
from models.centers_model import Center
from db import db  # Assuming db is your SQLAlchemy instance
import base64


class User(db.Model):
    __tablename__ = 'users'  # The table name as per your database schema
    __table_args__ = {'schema': 'u704613426_reports'}

    # Fields in the User model
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    first_name = Column(String(255), nullable=True)
    last_name = Column(String(255), nullable=True)
    email = Column(String(255), nullable=False, unique=True)
    username = Column(String(255), nullable=False, unique=True)
    password = Column(String(255), nullable=True)  # New password field
    role = Column(String(50), nullable=True)
    position = Column(String(255), nullable=True)
    image = Column(LargeBinary, nullable=True)
    clicked = Column(Text, nullable=True)
    deactivated = Column(Boolean, default=False)
    deleted = Column(Boolean, default=False)
    first_login = db.Column(db.Boolean, default=True)
    created_time = Column(DateTime, default=datetime.utcnow)
    center_id = db.Column(db.Integer, db.ForeignKey(Center.id))

    # Relationship example (if needed)
    # reports = db.relationship('Report', backref='users', cascade='all, delete-orphan', lazy='dynamic')

    def __repr__(self):
        return f"<User(id={self.id}, username={self.username}, email={self.email})>"

    # to_dict function to convert the user instance to a dictionary
    def to_dict(self):
        return {
            "id": self.id,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "email": self.email,
            "username": self.username,
            "role": self.role,
            "position": self.position,
            "image": f"data:image/png;base64,{base64.b64encode(self.image).decode('utf-8')}" if self.image else None,
            "deactivated": self.deactivated,
            "deleted": self.deleted,
            "first_login": self.first_login,
            "center_id": self.center_id,
            "created_time": self.created_time.strftime('%Y-%m-%d %H:%M:%S'),
        }
