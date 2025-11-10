from extensions import db
from sqlalchemy import Index
from datetime import datetime

class MyWittiLot(db.Model):
    __tablename__ = 'mywitti_lots'
    __table_args__ = (
        Index('idx_lots_available', 'category_id', 'jetons', postgresql_where=db.text('stock > 0')),
        Index('idx_lots_category', 'category_id'),
        Index('idx_lots_category_jetons', 'category_id', 'jetons'),
        Index('idx_lots_jetons', 'jetons'),
        Index('idx_lots_libelle', 'libelle'),
        Index('idx_lots_stock', 'stock'),
    )

    id = db.Column(db.Integer, primary_key=True)
    libelle = db.Column(db.String(255), nullable=False)
    slug = db.Column(db.Text)
    jetons = db.Column(db.Integer, default=0)
    stock = db.Column(db.Integer, default=0)
    recompense_image = db.Column(db.String(255))
    category_id = db.Column(db.Integer, db.ForeignKey('mywitti_category.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    category = db.relationship("MyWittiCategory", backref="lots")