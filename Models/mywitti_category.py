from extensions import db
from sqlalchemy.schema import UniqueConstraint
from sqlalchemy import Index
from datetime import datetime

class MyWittiCategory(db.Model):
    __tablename__ = 'mywitti_category'
    __table_args__ = (
        UniqueConstraint('slug', name='category_slug_key'),
        Index('idx_category_level', 'level'),
        Index('idx_category_level_min_jetons', 'level', 'min_jetons'),
        Index('idx_category_min_jetons', 'min_jetons'),
        Index('idx_category_name', 'category_name'),
    )
    id = db.Column(db.Integer, primary_key=True)
    category_name = db.Column(db.String(100), nullable=False)
    slug = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.Text)
    categ_points = db.Column(db.Integer, default=0)
    recompense_point = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    level = db.Column(db.Integer, nullable=False, default=1)
    min_jetons = db.Column(db.BigInteger, nullable=False, default=0)
    nb_jours = db.Column(db.Integer, nullable=False, default=90)
