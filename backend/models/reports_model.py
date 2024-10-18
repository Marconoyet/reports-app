from sqlalchemy import Column, BigInteger, String, LargeBinary, DateTime, ForeignKey
from db import db
from datetime import datetime
from models.users_model import User
from models.template_model import Template
import base64
class Report(db.Model):
    __tablename__ = 'reports'
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    report_name = Column(String(255), nullable=False)  # Name of the report
    report_file = Column(LargeBinary, nullable=True)  # BLOB to store the report file
    report_image = Column(LargeBinary, nullable=True)  # BLOB to store report image
    user_id = Column(BigInteger, ForeignKey(User.id), nullable=False)  # Foreign key referencing users table
    template_id = Column(BigInteger, ForeignKey(Template.id), nullable=False)  # Foreign key referencing templates table
    created_time = Column(DateTime, default=datetime.utcnow)  # Timestamp for when the report was created
    user = db.relationship("User")
    def __repr__(self):
        return f"<Report(id={self.id}, report_name={self.report_name}, created_time={self.created_time})>"

    def to_dict(self):
        """Convert the report instance to a dictionary."""
        return {
            "id": self.id,
            "report_name": self.report_name,
            "user": {
                "name": f"{self.user.first_name or ''} {self.user.last_name or ''}".strip(),  # Handles None and removes extra spaces
                "email": self.user.email or ''  # Provide an empty string if email is None
            },
            "report_image": f"data:image/png;base64,{base64.b64encode(self.report_image).decode('utf-8')}" if self.report_image else None,  # Encode image as Base64
            "createdTime": {
                "date": self.created_time.strftime('%Y-%m-%d'),
                "time": self.created_time.strftime('%H:%M:%S')
            }
        }