from extensions import db
from datetime import datetime

class MyWittiNotification(db.Model):
    __tablename__ = 'mywitti_notification'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)    
    user_id = db.Column(db.Integer, db.ForeignKey('mywitti_users.id'), nullable=False)
    message = db.Column(db.String, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_read = db.Column(db.Boolean, default=False)

    user = db.relationship('MyWittiUser', backref='notifications') 