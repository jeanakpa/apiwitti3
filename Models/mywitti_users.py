# Models/mywitti_users.py

from extensions import db
from datetime import datetime
import bcrypt
from sqlalchemy import Index, CheckConstraint
from Models.mywitti_user_type import MyWittiUserType  # ✅ Import explicite du modèle lié


class MyWittiUser(db.Model):
    __tablename__ = 'mywitti_users'
    __table_args__ = (
        db.UniqueConstraint('user_id', name='users_user_id_key'),
        Index('idx_mywitti_users_user_type_id', 'user_type_id'),
        Index('idx_users_active', 'user_id', postgresql_where=db.text('is_active = true')),
        Index('idx_users_date_joined', 'date_joined'),
        Index('idx_users_last_login', 'last_login'),
        Index('idx_users_type_active', 'user_type', 'is_active'),
        Index('idx_users_user_type', 'user_type'),
        CheckConstraint("user_type IN ('client', 'admin', 'superadmin')", name='users_user_type_check'),
    )

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.Text, nullable=False)
    first_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100))
    email = db.Column(db.String(255))

    # ✅ Liaison à la table MyWittiUserType
    user_type_id = db.Column(db.Integer, db.ForeignKey('mywitti_user_type.id'))
    user_type_rel = db.relationship('MyWittiUserType', backref='users', lazy='joined')

    # ✅ Type logique (client, admin, superadmin)
    user_type = db.Column(db.String(20), default='client')

    # ✅ Infos de statut
    date_joined = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    is_active = db.Column(db.Boolean, default=True)
    is_staff = db.Column(db.Boolean, default=False)
    must_change_password = db.Column(db.Boolean, default=True)

    # =====================================================
    # Gestion du mot de passe (bcrypt)
    # =====================================================
    def set_password(self, password: str):
        """Hash et définit le mot de passe de l'utilisateur"""
        hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        self.password = hashed.decode('utf-8')

    def check_password(self, password: str) -> bool:
        """Vérifie le mot de passe saisi"""
        try:
            return bcrypt.checkpw(password.encode('utf-8'), self.password.encode('utf-8'))
        except ValueError:
            # Si le mot de passe en base n'est pas un hash valide (ancien format)
            return False

    # =====================================================
    # Rôles utilisateur
    # =====================================================
    @property
    def is_admin(self):
        """Retourne True si l'utilisateur est un admin"""
        return self.user_type == 'admin'

    @property
    def is_superuser(self):
        """Retourne True si l'utilisateur est un super admin"""
        return self.user_type == 'superadmin'

    # =====================================================
    # Représentation utile pour le debug
    # =====================================================
    def __repr__(self):
        return f"<MyWittiUser {self.email or self.user_id} ({self.user_type})>"
