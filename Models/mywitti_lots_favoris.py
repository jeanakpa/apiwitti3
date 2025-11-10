from extensions import db
from sqlalchemy import Index
from datetime import datetime

class MyWittiLotsFavoris(db.Model):
    __tablename__ = 'mywitti_lots_favoris'
    __table_args__ = (
        db.UniqueConstraint('client_id', 'lot_id', name='unique_client_lot_favoris'),
        Index('idx_favoris_client_lot', 'client_id', 'lot_id'),
        Index('idx_favoris_client_lot_date', 'client_id', 'lot_id', 'date_ajout'),
    )
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.BigInteger, db.ForeignKey('mywitti_client.id', ondelete='CASCADE'), nullable=False)
    lot_id = db.Column(db.Integer, db.ForeignKey('mywitti_lots.id', ondelete='CASCADE'), nullable=False)
    date_ajout = db.Column(db.DateTime, default=datetime.utcnow)
    client = db.relationship('MyWittiClient', backref='favoris')
    lot = db.relationship('MyWittiLot', backref='favoris')