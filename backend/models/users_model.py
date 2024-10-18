from sqlalchemy import Column, BigInteger, String, DateTime, Boolean, Text
from datetime import datetime
from db import db  # Assuming db is your SQLAlchemy instance

class User(db.Model):
    __tablename__ = 'users'  # The table name as per your database schema
    __table_args__= {'schema':'u704613426_reports'}
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    first_name = Column(String(255), nullable=True)
    last_name = Column(String(255), nullable=True)
    email = Column(String(255), nullable=False, unique=True)
    username = Column(String(255), nullable=False, unique=True)
    role = Column(String(50), nullable=True)
    position = Column(String(255), nullable=True)
    clicked = Column(Text, nullable=True)
    deactivated = Column(Boolean, default=False)
    deleted = Column(Boolean, default=False)
    created_time = Column(DateTime, default=datetime.utcnow)
    # reports = db.relationship('Report', backref = 'users', cascade = 'all, delete-orphan', lazy = 'dynamic')
    def __repr__(self):
        return f"<User(id={self.id}, username={self.username}, email={self.email})>"
