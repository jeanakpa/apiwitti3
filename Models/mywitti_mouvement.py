from extensions import db
from sqlalchemy import Index
from datetime import date

class MyWittiMouvement(db.Model):
    __tablename__ = 'mywitti_mouvement'
    __table_args__ = (
        db.UniqueConstraint('reference', name='mywitti_mouvement_reference_key'),
        Index('idx_mouvement_account_number', 'account_number'),
        Index('idx_mouvement_booking_date', 'booking_date'),
        Index('idx_mouvement_customer_code', 'customer_code'),
    )
    id = db.Column(db.Integer, primary_key=True)
    libelle = db.Column(db.String(255), nullable=True)
    customer_code = db.Column(db.String(50), nullable=False)
    account_number = db.Column(db.String(50), nullable=False)
    booking_date = db.Column(db.Date, nullable=False)
    reference = db.Column(db.String(100), nullable=False, unique=True)
    debit = db.Column(db.BigInteger)
    credit = db.Column(db.BigInteger)