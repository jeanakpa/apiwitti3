from extensions import db
from sqlalchemy import Index
from datetime import datetime

class MyWittiClientJetonsStabilite(db.Model):
    __tablename__ = 'mywitti_client_jetons_stabilite'
    __table_args__ = (
        db.UniqueConstraint('client_id', 'mois_annee', name='mywitti_client_jetons_stabilite_client_id_mois_annee_key'),
        Index('idx_jetons_stabilite_client_mois', 'client_id', 'mois_annee'),
    )
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.BigInteger, db.ForeignKey('mywitti_client.id'), nullable=False)
    mois_annee = db.Column(db.String(7), nullable=False)
    moyenne_solde = db.Column(db.BigInteger, nullable=False)
    jetons_stabilite = db.Column(db.BigInteger, nullable=False)
    reliquat = db.Column(db.BigInteger, default=0)
    date_calcul = db.Column(db.DateTime, default=datetime.utcnow)
    client = db.relationship('MyWittiClient', backref='jetons_stabilite') 