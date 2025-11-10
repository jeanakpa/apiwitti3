from extensions import db
from sqlalchemy import Index
from datetime import datetime

class MyWittiJetonsTransactions(db.Model):
    __tablename__ = 'mywitti_jetons_transactions'
    __table_args__ = (
        Index('idx_jetons_transactions_type', 'type_transaction'),
        Index('idx_transactions_client_date_montant', 'client_id', 'date_transaction', 'montant'),
        Index('idx_transactions_date_montant', 'date_transaction', 'montant'),
        Index('idx_transactions_lot', 'lot_id'),
        Index('idx_transactions_montant', 'montant'),
    )
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.BigInteger, db.ForeignKey('mywitti_client.id', ondelete='CASCADE'), nullable=False)
    lot_id = db.Column(db.Integer, db.ForeignKey('mywitti_lots.id', ondelete='SET NULL'))
    montant = db.Column(db.Integer, nullable=False)
    motif = db.Column(db.Text)
    date_transaction = db.Column(db.DateTime, default=datetime.utcnow)
    type_transaction = db.Column(db.String(30), default='operation')
    reliquat = db.Column(db.BigInteger, default=0)
    client = db.relationship('MyWittiClient', backref='transactions')
    lot = db.relationship('MyWittiLot', backref='transactions') 