# seed_admin.py
from extensions import db
from Account.models import Admin
from app import create_app

app = create_app()

with app.app_context():
    existing_admin = Admin.query.filter_by(email='mister@gmail.com').first()
    if existing_admin:
        print("L'administrateur existe déjà.")
    else:
        admin = Admin(
            name='Admin test',
            email='mister@gmail.com',
            role='Admin',
            password='mywitti'  # Le mot de passe est requis
        )
        db.session.add(admin)
        db.session.commit()
        print("Admin ajouté avec succès.")
