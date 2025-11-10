from extensions import db
from datetime import datetime
from sqlalchemy import Index

class MyWittiAdvertisement(db.Model):
    __tablename__ = 'mywitti_advertisements'
    __table_args__ = (
        Index('idx_advertisements_active', 'is_active'),
        Index('idx_advertisements_country', 'country'),
        Index('idx_advertisements_created_at', 'created_at'),
        Index('idx_advertisements_active_country', 'is_active', 'country'),
    )

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    image_url = db.Column(db.Text, nullable=False)
    country = db.Column(db.String(100), nullable=True)  # NULL = tous les pays
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('mywitti_users.id', ondelete='SET NULL'))

    # Relation avec l'utilisateur qui a créé la publicité
    creator = db.relationship('MyWittiUser', backref='advertisements')

    def to_dict(self):
        """Convertit l'objet en dictionnaire pour l'API"""
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'image_url': self.image_url,
            'country': self.country,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'created_by': self.created_by
        }

