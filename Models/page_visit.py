#Models/page_visit.py

# models/page_visit.py
from extensions import db
from datetime import datetime

# Models/page_visit.py
class PageVisit(db.Model):
    __tablename__ = 'page_visit'  # <- IMPORTANT : ce nom doit correspondre à la requête

    id = db.Column(db.Integer, primary_key=True)
    path = db.Column(db.String(255), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer)
    user_type = db.Column(db.String(50))  # 'admin' ou 'customer'

    def __repr__(self):
        return f"<PageVisit path={self.path} timestamp={self.timestamp}>"
