from extensions import db
from datetime import datetime

class MyWittiSupportRequest(db.Model):
    __tablename__ = "mywitti_support_request"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("mywitti_users.id"), nullable=False)
    subject = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=False)
    request_type = db.Column(db.String(50), nullable=False)  # Reclamation / Assistance / Autre
    status = db.Column(db.String(50), default='Pending', nullable=False)
    response = db.Column(db.Text, nullable=True)  # réponse de l’admin
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)

    user = db.relationship("MyWittiUser", backref="support_requests")

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "subject": self.subject,
            "description": self.description,
            "request_type": self.request_type,
            "status": self.status,
            "response": self.response,
            "created_at": self.created_at.strftime("%d-%m-%Y %H:%M:%S") if self.created_at else None,
            "updated_at": self.updated_at.strftime("%d-%m-%Y %H:%M:%S") if self.updated_at else None
        }
