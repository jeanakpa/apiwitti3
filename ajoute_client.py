#!/usr/bin/env python3
"""
Script pour créer un utilisateur client simple avec identifiant 123456
"""
import sys
import os
from datetime import datetime, date

# Configuration des variables d'environnement (AVANT l'import de app)
# Ces valeurs sont utilisées uniquement en développement local
if not os.environ.get('SECRET_KEY'):
    os.environ['SECRET_KEY'] = 'dev-secret-key-for-local-script-123456'
if not os.environ.get('JWT_SECRET_KEY'):
    os.environ['JWT_SECRET_KEY'] = 'dev-jwt-secret-key-for-local-script-123456'
if not os.environ.get('DATABASE_URL'):
    os.environ['DATABASE_URL'] = 'postgresql://postgres:mywitti@localhost:5432/mywitti'
if not os.environ.get('FLASK_ENV'):
    os.environ['FLASK_ENV'] = 'development'

# Ajouter le répertoire parent au path pour importer l'app
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from Models.mywitti_users import MyWittiUser
from Models.mywitti_user_type import MyWittiUserType
from Models.mywitti_client import MyWittiClient
from werkzeug.security import generate_password_hash

def fix_sequence():
    """Répare la séquence de l'ID de la table mywitti_client"""
    try:
        # Récupérer le MAX(id) actuel et mettre à jour la séquence
        result = db.session.execute(db.text("""
            SELECT setval('mywitti_client_id_seq', 
                         COALESCE((SELECT MAX(id) FROM mywitti_client), 0) + 1, 
                         false);
        """))
        db.session.commit()
        print("   ✅ Séquence de la table mywitti_client réparée")
    except Exception as e:
        print(f"   ⚠️  Erreur lors de la réparation de la séquence : {e}")
        db.session.rollback()

def ajouter_client():
    """Crée un utilisateur client avec identifiant 123456"""
    
    with app.app_context():
        try:
            print("=== CRÉATION D'UN CLIENT TEST ===")
            
            # Réparer la séquence avant de commencer
            print("\n0. Réparation de la séquence...")
            fix_sequence()
            
            # Créer l'utilisateur
            print("\n1. Vérification/Création de l'utilisateur...")
            identifiant = '123456'
            user_existant = MyWittiUser.query.filter_by(user_id=identifiant).first()
            
            if user_existant:
                print(f"   ⚠️  L'utilisateur avec l'identifiant '{identifiant}' existe déjà.")
                print(f"   - ID utilisateur: {user_existant.id}")
                # Mettre à jour le mot de passe si nécessaire
                user_existant.password = generate_password_hash('123456')
                user = user_existant
            else:
                # Vérifier si le type d'utilisateur 'client' existe
                user_type_client = MyWittiUserType.query.filter_by(type_name='client').first()
                if not user_type_client:
                    user_type_client = MyWittiUserType(
                        type_name='client',
                        description='Client standard',
                        permissions={'read_own': True, 'write_own': True},
                        is_active=True
                    )
                    db.session.add(user_type_client)
                    db.session.flush()
                    print("   - Type d'utilisateur 'client' créé")
                
                user = MyWittiUser(
                    user_id=identifiant,
                    password=generate_password_hash('123456'),
                    first_name='Client',
                    last_name='Test',
                    user_type='client',
                    is_active=True,
                    is_staff=False,
                    must_change_password=False,
                    user_type_id=user_type_client.id if user_type_client else 3,
                    email='test@example.com',
                    date_joined=datetime.utcnow()
                )
                db.session.add(user)
                db.session.flush()  # Pour obtenir l'ID
                print(f"   ✅ Utilisateur '{identifiant}' créé avec succès")
                print(f"   - ID utilisateur: {user.id}")
            
            # Créer le client associé
            print("\n2. Vérification/Création du client...")
            client_existant = MyWittiClient.query.filter_by(customer_code=identifiant).first()
            
            if client_existant:
                print(f"   ⚠️  Le client avec le code '{identifiant}' existe déjà.")
                print(f"   - ID client: {client_existant.id}")
                print(f"   - Nom: {client_existant.short_name} {client_existant.first_name}")
                # Vérifier si le client est lié à l'utilisateur
                if client_existant.user_id != user.id:
                    print(f"   - Mise à jour: liaison du client à l'utilisateur {user.id}")
                    client_existant.user_id = user.id
            else:
                # Utiliser une requête SQL brute pour éviter les champs définis dans le modèle
                try:
                    db.session.execute(db.text("""
                        INSERT INTO mywitti_client 
                        (customer_code, short_name, first_name, gender, birth_date, 
                         phone_number, street, jetons, date_ouverture, nombre_jours, 
                         category_id, user_id)
                        VALUES 
                        (:customer_code, :short_name, :first_name, :gender, :birth_date,
                         :phone_number, :street, :jetons, :date_ouverture, :nombre_jours,
                         :category_id, :user_id)
                    """), {
                        'customer_code': identifiant,
                        'short_name': 'test',
                        'first_name': 'Client Test',
                        'gender': 'M',
                        'birth_date': date(1990, 1, 15),
                        'phone_number': '+22501234567',
                        'street': '123 Rue de Test, Abidjan, Côte d\'Ivoire',
                        'jetons': 0,
                        'date_ouverture': datetime.utcnow().strftime('%Y-%m-%d'),
                        'nombre_jours': '30',
                        'category_id': 1,
                        'user_id': user.id
                    })
                    print(f"   ✅ Client créé avec succès")
                    print(f"   - Code client: {identifiant}")
                    print(f"   - Nom: test Client Test")
                except Exception as e:
                    print(f"   ❌ Erreur lors de l'insertion : {e}")
                    raise
            
            # Valider toutes les modifications
            db.session.commit()
            print("\n✅ Client créé avec succès !")
            print(f"\nInformations de connexion:")
            print(f"   - Identifiant: {identifiant}")
            print(f"   - Mot de passe: 123456")
            print(f"   - Type: Client")
            
        except Exception as e:
            db.session.rollback()
            print(f"\n❌ Erreur lors de la création du client : {str(e)}")
            import traceback
            traceback.print_exc()
            raise

if __name__ == "__main__":
    ajouter_client()