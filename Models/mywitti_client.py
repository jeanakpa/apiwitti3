#Models/mywitti_client.py

from extensions import db
from sqlalchemy import Index
from datetime import date

class MyWittiClient(db.Model):
    __tablename__ = 'mywitti_client'
    __table_args__ = (
        db.UniqueConstraint('customer_code', name='mywitti_client_ukey'),
        Index('idx_client_active', 'customer_code', postgresql_where=db.text('jetons > 0')),
        Index('idx_client_category_jetons', 'category_id', 'jetons'),
        Index('idx_client_customer_code', 'customer_code'),
        Index('idx_client_first_name', 'first_name'),
        Index('idx_client_name_search', 'first_name', 'short_name'),
        Index('idx_client_phone_number', 'phone_number'),
        Index('idx_client_user_id', 'user_id'),
        Index('idx_client_working_balance', 'working_balance'),
    )
    id = db.Column(db.BigInteger, primary_key=True)
    customer_code = db.Column(db.String(10), nullable=False, unique=True)
    short_name = db.Column(db.String(50))
    first_name = db.Column(db.String(100))
    gender = db.Column(db.String(50))
    birth_date = db.Column(db.Date)
    phone_number = db.Column(db.String(100))
    street = db.Column(db.String(100))
    jetons = db.Column(db.BigInteger)
    date_ouverture = db.Column(db.String(100))
    nombre_jours = db.Column(db.String(50))
    category_id = db.Column(db.Integer, db.ForeignKey('mywitti_category.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('mywitti_users.id', onupdate='CASCADE', ondelete='SET NULL'))
    working_balance = db.Column(db.BigInteger, default=0)
    reliquat_transaction = db.Column(db.BigInteger, default=0)
    reliquat_stabilite = db.Column(db.BigInteger, default=0)
    jetons_transaction = db.Column(db.BigInteger, default=0)
    jetons_stabilite = db.Column(db.BigInteger, default=0)
    category = db.relationship('MyWittiCategory', backref='clients')
    user = db.relationship('MyWittiUser', backref='clients')
