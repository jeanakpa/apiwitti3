from extensions import db
from sqlalchemy import Index
from datetime import date

class MyWittiClientPalierHistory(db.Model):
    __tablename__ = 'mywitti_client_palier_history'
    __table_args__ = (
        Index('idx_palier_history_active', 'client_id', 'date_debut', postgresql_where=db.text("statut = 'en_cours'")),
        Index('idx_palier_history_client_date', 'client_id', 'date_debut'),
        Index('idx_palier_history_client_period', 'client_id', 'date_debut', 'date_fin'),
        Index('idx_palier_history_date_fin', 'date_fin'),
        Index('idx_palier_history_statut', 'statut'),
    )
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.BigInteger, db.ForeignKey('mywitti_client.id'), nullable=False)
    palier = db.Column(db.String(50), nullable=False)
    date_debut = db.Column(db.Date, nullable=False)
    date_fin = db.Column(db.Date)
    statut = db.Column(db.String(20), nullable=False, default='en_cours')
    client = db.relationship('MyWittiClient', backref='palier_history') 