#!/usr/bin/env python3
import os
from app import app
from extensions import db
from Models.mywitti_users import MyWittiUser
from Models.mywitti_category import MyWittiCategory
from werkzeug.security import generate_password_hash
from datetime import datetime

# Configuration des variables d'environnement
os.environ['SECRET_KEY'] = 'test-secret-key-123'
os.environ['JWT_SECRET_KEY'] = 'test-jwt-secret-key-123'
os.environ['DATABASE_URL'] = 'sqlite:///instance/mywitti.db'

with app.app_context():
    print("=== INITIALISATION DE LA BASE DE DONNÉES ===")
    
    # Créer toutes les tables
    try:
        db.create_all()
        print("✓ Tables créées avec succès")
    except Exception as e:
        print(f"✗ Erreur lors de la création des tables: {str(e)}")
        exit(1)
    
    # Créer les catégories de base
    categories_data = [
        {"name": "Eco Premium", "code": "A", "min": 0, "max": 100},
        {"name": "Executive", "code": "B", "min": 100, "max": 1000},
        {"name": "Executive +", "code": "C", "min": 1000, "max": 3000},
        {"name": "First Class", "code": "D", "min": 3000, "max": float('inf')}
    ]
    
    for cat_data in categories_data:
        existing = MyWittiCategory.query.filter_by(category_name=cat_data["name"]).first()
        if not existing:
            category = MyWittiCategory(
                category_name=cat_data["name"],
                slug=cat_data["code"].lower(),
                level=cat_data["min"],
                min_jetons=cat_data["min"],
                nb_jours=30
            )
            db.session.add(category)
            print(f"✓ Catégorie '{cat_data['name']}' créée")
        else:
            print(f"✓ Catégorie '{cat_data['name']}' existe déjà")
    
    # Créer un superadmin de test
    superadmin_email = "superadmin@test.com"
    superadmin_user_id = "superadmin"
    
    existing_admin = MyWittiUser.query.filter_by(email=superadmin_email).first()
    if not existing_admin:
        superadmin = MyWittiUser(
            first_name="Super",
            last_name="Admin",
            email=superadmin_email,
            user_id=superadmin_user_id,
            password_hash=generate_password_hash("password123"),
            is_admin=True,
            is_superuser=True,
            is_active=True,
            created_at=datetime.utcnow()
        )
        db.session.add(superadmin)
        print("✓ Superadmin créé avec succès")
        print(f"  Email: {superadmin_email}")
        print(f"  User ID: {superadmin_user_id}")
        print(f"  Password: password123")
    else:
        print("✓ Superadmin existe déjà")
        print(f"  Email: {superadmin_email}")
        print(f"  User ID: {superadmin_user_id}")
    
    # Créer un admin normal de test
    admin_email = "admin@test.com"
    admin_user_id = "admin"
    
    existing_admin = MyWittiUser.query.filter_by(email=admin_email).first()
    if not existing_admin:
        admin = MyWittiUser(
            first_name="Admin",
            last_name="Test",
            email=admin_email,
            user_id=admin_user_id,
            password_hash=generate_password_hash("password123"),
            is_admin=True,
            is_superuser=False,
            is_active=True,
            created_at=datetime.utcnow()
        )
        db.session.add(admin)
        print("✓ Admin créé avec succès")
        print(f"  Email: {admin_email}")
        print(f"  User ID: {admin_user_id}")
        print(f"  Password: password123")
    else:
        print("✓ Admin existe déjà")
        print(f"  Email: {admin_email}")
        print(f"  User ID: {admin_user_id}")
    
    # Valider toutes les modifications
    try:
        db.session.commit()
        print("\n✓ Base de données initialisée avec succès!")
        
        # Vérifier les administrateurs
        admins = MyWittiUser.query.filter(
            (MyWittiUser.is_admin == True) | (MyWittiUser.is_superuser == True)
        ).all()
        
        print(f"\n=== ADMINISTRATEURS DISPONIBLES ({len(admins)}) ===")
        for admin in admins:
            print(f"  - {admin.first_name} {admin.last_name}")
            print(f"    Email: {admin.email}")
            print(f"    User ID: {admin.user_id}")
            print(f"    Admin: {admin.is_admin}, Superuser: {admin.is_superuser}")
            print()
            
    except Exception as e:
        print(f"✗ Erreur lors de la validation: {str(e)}")
        db.session.rollback()
        exit(1)
    
    print("=== FIN DE L'INITIALISATION ===") 