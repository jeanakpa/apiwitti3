from extensions import db
from sqlalchemy import Index
from datetime import datetime

class MyWittiLotsClaims(db.Model):
    __tablename__ = 'mywitti_lots_claims'
    __table_args__ = (
        Index('idx_claims_client_lot', 'client_id', 'lot_id'),
        Index('idx_claims_client_statut', 'client_id', 'statut'),
        Index('idx_claims_date', 'date_reclamation'),
        Index('idx_claims_pending', 'client_id', 'date_reclamation', postgresql_where=db.text("statut = 'en_attente'")),
        Index('idx_claims_statut', 'statut'),
    )
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.BigInteger, db.ForeignKey('mywitti_client.id', ondelete='CASCADE'), nullable=False)
    lot_id = db.Column(db.Integer, db.ForeignKey('mywitti_lots.id', ondelete='CASCADE'), nullable=False)
    date_reclamation = db.Column(db.DateTime, default=datetime.utcnow)
    statut = db.Column(db.String(50), default='en_attente')
    client = db.relationship('MyWittiClient', backref='claims')
    lot = db.relationship('MyWittiLot', backref='claims')