import os
from flask import Flask
from werkzeug.security import generate_password_hash
from extensions import db
from Models.mywitti_users import MyWittiUser

def create_superadmin():
    app = Flask(__name__)
    
    # Configuration minimale pour que SQLAlchemy et JWT fonctionnent
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL') or 'sqlite:///mywitti.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY') or 'mysecretkey123'
    
    db.init_app(app)

    with app.app_context():
        email = "super@gmail.com"
        password = "123456"

        # Vérifier si le superadmin existe déjà
        existing = MyWittiUser.query.filter_by(email=email).first()
        if existing:
            print(f"L'utilisateur {email} existe déjà.")
            return

        # Créer le superadmin
        superadmin = MyWittiUser(
            email=email,
            password=generate_password_hash(password),
            is_admin=True,
            is_superuser=True
        )
        db.session.add(superadmin)
        db.session.commit()
        print(f"Super Admin '{email}' créé avec succès !")

if __name__ == "__main__":
    create_superadmin()
