from extensions import db
from sqlalchemy import Index
from datetime import date

class MyWittiClientJetonsDaily(db.Model):
    __tablename__ = 'mywitti_client_jetons_daily'
    __table_args__ = (
        Index('idx_daily_client_date_solde', 'client_id', 'date_jour', 'solde_jetons'),
        Index('idx_daily_date_solde', 'date_jour', 'solde_jetons'),
    )
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.BigInteger, db.ForeignKey('mywitti_client.id'), nullable=False)
    date_jour = db.Column(db.Date, nullable=False)
    solde_jetons = db.Column(db.BigInteger, nullable=False)
    client = db.relationship('MyWittiClient', backref='jetons_daily') 