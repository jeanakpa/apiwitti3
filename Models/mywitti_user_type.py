# Models/mywitti_user_type.py
from extensions import db
from datetime import datetime

class MyWittiUserType(db.Model):
    __tablename__ = 'mywitti_user_type'
    __table_args__ = (
        db.UniqueConstraint('type_name', name='mywitti_user_type_type_name_key'),
    )

    id = db.Column(db.Integer, primary_key=True)
    type_name = db.Column(db.String(50), nullable=False, unique=True)
    description = db.Column(db.Text)
    permissions = db.Column(db.JSON, default={})
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<MyWittiUserType {self.type_name}>"