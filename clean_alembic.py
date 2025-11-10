#!/usr/bin/env python3
"""
Script pour nettoyer la table alembic_version et permettre de recommencer les migrations
"""
import os
import sys
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

def clean_alembic_version():
    """Nettoie la table alembic_version"""
    app = Flask(__name__)
    
    # Configuration directe pour éviter les problèmes de variables d'environnement
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:mywitti@localhost:5432/mywitti'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = 'temp-secret-key-for-cleaning'
    
    db = SQLAlchemy(app)
    
    with app.app_context():
        try:
            # Supprimer la table alembic_version si elle existe
            db.engine.execute("DROP TABLE IF EXISTS alembic_version")
            print("✅ Table alembic_version supprimée avec succès")
            
            # Vérifier que la table n'existe plus
            result = db.engine.execute("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'alembic_version')")
            exists = result.fetchone()[0]
            
            if not exists:
                print("✅ Confirmation : la table alembic_version n'existe plus")
            else:
                print("❌ La table alembic_version existe encore")
                
        except Exception as e:
            print(f"❌ Erreur lors du nettoyage : {e}")
            return False
            
    return True

if __name__ == "__main__":
    print("🧹 Nettoyage de la table alembic_version...")
    if clean_alembic_version():
        print("✅ Nettoyage terminé. Vous pouvez maintenant relancer 'flask db migrate'")
    else:
        print("❌ Échec du nettoyage")
        sys.exit(1) 