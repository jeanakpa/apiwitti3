#!/usr/bin/env python3
"""
Script pour créer la migration de la table des publicités
"""

import os
import sys
from flask import Flask
from flask_migrate import Migrate
from extensions import db
from Models.mywitti_advertisement import MyWittiAdvertisement

# Configuration de l'application Flask
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'postgresql://username:password@localhost/mywitti_db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialisation des extensions
db.init_app(app)
migrate = Migrate(app, db)

def create_migration():
    """Créer la migration pour la table des publicités"""
    try:
        with app.app_context():
            # Vérifier si la table existe déjà
            inspector = db.inspect(db.engine)
            if 'mywitti_advertisements' in inspector.get_table_names():
                print("La table mywitti_advertisements existe déjà.")
                return
            
            # Créer la table
            db.create_all()
            print("Migration créée avec succès!")
            print("Table mywitti_advertisements ajoutée à la base de données.")
            
    except Exception as e:
        print(f"Erreur lors de la création de la migration: {e}")
        sys.exit(1)

if __name__ == '__main__':
    create_migration() 