# models/mywitti_referral.py
from extensions import db
from datetime import datetime

class MyWittiReferral(db.Model):
    __tablename__ = 'mywitti_referral'
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    referrer_id = db.Column(db.BigInteger, db.ForeignKey('mywitti_users.id'), nullable=False)
    referred_email = db.Column(db.String(255), nullable=False)
    referral_code = db.Column(db.String(50), nullable=False, unique=True)
    status = db.Column(db.String(20), nullable=False, default='pending')
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    referrer = db.relationship('MyWittiUser', backref='referrals')

    def to_dict(self):
        return {
            "id": self.id,
            "referrer_id": self.referrer_id,
            "referred_email": self.referred_email,
            "referral_code": self.referral_code,
            "status": self.status,
            "created_at": self.created_at.isoformat(),
            "referrer": {
                "id": self.referrer.id,
                "user_id": self.referrer.user_id,
                "email": self.referrer.email
            } if self.referrer else None
        }

    def __repr__(self):
        return f"<MyWittiReferral referrer_id={self.referrer_id} referred_email={self.referred_email} status={self.status}>" 