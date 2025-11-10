from extensions import db
from sqlalchemy import Index
from datetime import date

class MyWittiCompte(db.Model):
    __tablename__ = 'mywitti_comptes'
    __table_args__ = (
        db.UniqueConstraint('numero_compte', name='mywitti_comptes_ukey'),
        Index('idx_comptes_agence', 'agence'),
        Index('idx_comptes_balance', 'working_balance'),
        Index('idx_comptes_customer', 'customer_code'),
        Index('idx_comptes_customer_balance', 'customer_code', 'working_balance'),
        Index('idx_comptes_numero', 'numero_compte'),
        Index('idx_comptes_positive_balance', 'customer_code', 'working_balance', postgresql_where=db.text('working_balance > 0')),
    )
    id = db.Column(db.Integer, primary_key=True)
    customer_code = db.Column(db.String(50), db.ForeignKey('mywitti_client.customer_code', ondelete='CASCADE'), nullable=False)
    agence = db.Column(db.String(100))
    numero_compte = db.Column(db.String(50), nullable=False, unique=True)
    libelle = db.Column(db.String(100))
    date_ouverture_compte = db.Column(db.Date, nullable=False)
    working_balance = db.Column(db.BigInteger, default=0)
    client = db.relationship('MyWittiClient', backref='comptes', primaryjoin='MyWittiCompte.customer_code==MyWittiClient.customer_code') 