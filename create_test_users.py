#!/usr/bin/env python3
"""
Script pour créer les utilisateurs de test dans la base de données
"""
import sys
import os
from datetime import datetime, timedelta

# Ajouter le répertoire parent au path pour importer l'app
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from Models.mywitti_users import MyWittiUser
from Models.mywitti_user_type import MyWittiUserType
from Models.mywitti_category import MyWittiCategory
from Models.mywitti_client import MyWittiClient
from Models.mywitti_lots import MyWittiLot
from Models.mywitti_jetons_transactions import MyWittiJetonsTransactions
from Models.mywitti_notification import MyWittiNotification
from Models.mywitti_faq import MyWittiFAQ
from Models.mywitti_survey import MyWittiSurvey, MyWittiSurveyOption
from werkzeug.security import generate_password_hash

def create_test_data():
    """Crée toutes les données de test"""
    
    with app.app_context():
        try:
            print("=== CRÉATION DES DONNÉES DE TEST ===")
            
            # 1. Créer les types d'utilisateurs
            print("1. Création des types d'utilisateurs...")
            user_types = [
                MyWittiUserType(
                    id=1,
                    type_name='superadmin',
                    description='Super administrateur avec tous les droits',
                    permissions={'all': True},
                    is_active=True
                ),
                MyWittiUserType(
                    id=2,
                    type_name='admin',
                    description='Administrateur avec droits limités',
                    permissions={'read': True, 'write': True, 'delete': False},
                    is_active=True
                ),
                MyWittiUserType(
                    id=3,
                    type_name='client',
                    description='Client standard',
                    permissions={'read_own': True, 'write_own': True},
                    is_active=True
                )
            ]
            
            for user_type in user_types:
                existing = MyWittiUserType.query.get(user_type.id)
                if not existing:
                    db.session.add(user_type)
                    print(f"   - Type '{user_type.type_name}' créé")
                else:
                    print(f"   - Type '{user_type.type_name}' existe déjà")
            
            # 2. Créer les catégories
            print("\n2. Création des catégories...")
            categories = [
                MyWittiCategory(
                    id=1,
                    category_name='Eco Premium',
                    slug='eco-premium',
                    description='Catégorie Eco Premium (1 à 99 jetons)',
                    categ_points=10,
                    recompense_point=5,
                    level=1,
                    min_jetons=1,
                    nb_jours=30
                ),
                MyWittiCategory(
                    id=2,
                    category_name='Executive',
                    slug='executive',
                    description='Catégorie Executive (100 à 999 jetons)',
                    categ_points=50,
                    recompense_point=25,
                    level=2,
                    min_jetons=100,
                    nb_jours=60
                ),
                MyWittiCategory(
                    id=3,
                    category_name='Executive +',
                    slug='executive-plus',
                    description='Catégorie Executive + (1000 à 3000 jetons)',
                    categ_points=100,
                    recompense_point=50,
                    level=3,
                    min_jetons=1000,
                    nb_jours=90
                ),
                MyWittiCategory(
                    id=4,
                    category_name='First Class',
                    slug='first-class',
                    description='Catégorie First Class (+ de 3000 jetons)',
                    categ_points=200,
                    recompense_point=100,
                    level=4,
                    min_jetons=3000,
                    nb_jours=120
                )
            ]
            
            for category in categories:
                existing = MyWittiCategory.query.get(category.id)
                if not existing:
                    db.session.add(category)
                    print(f"   - Catégorie '{category.category_name}' créée")
                else:
                    print(f"   - Catégorie '{category.category_name}' existe déjà")
            
            # 3. Créer l'utilisateur superadmin
            print("\n3. Création de l'utilisateur superadmin...")
            superadmin = MyWittiUser.query.filter_by(email='superadmin@gmail.com').first()
            if not superadmin:
                superadmin = MyWittiUser(
                    id=1,
                    user_id='superadmin',
                    password=generate_password_hash('123456'),
                    first_name='Super',
                    last_name='Admin',
                    user_type='superadmin',
                    is_active=True,
                    is_staff=True,
                    must_change_password=False,
                    user_type_id=1,
                    email='superadmin@gmail.com'
                )
                db.session.add(superadmin)
                print("   - Utilisateur superadmin créé")
            else:
                print("   - Utilisateur superadmin existe déjà")
            
            # 4. Créer l'utilisateur client de test
            print("\n4. Création de l'utilisateur client de test...")
            user_test = MyWittiUser.query.filter_by(email='user_test@gmail.com').first()
            if not user_test:
                user_test = MyWittiUser(
                    id=2,
                    user_id='user_test',
                    password=generate_password_hash('123456'),
                    first_name='User',
                    last_name='Test',
                    user_type='client',
                    is_active=True,
                    is_staff=False,
                    must_change_password=False,
                    user_type_id=3,
                    email='user_test@gmail.com'
                )
                db.session.add(user_test)
                print("   - Utilisateur user_test créé")
            else:
                print("   - Utilisateur user_test existe déjà")
            
            # 5. Créer le client associé à user_test
            print("\n5. Création du client associé...")
            client_test = MyWittiClient.query.filter_by(customer_code='user_test').first()
            if not client_test:
                client_test = MyWittiClient(
                    id=1,
                    customer_code='user_test',
                    short_name='Test',
                    first_name='User',
                    gender='M',
                    birth_date=datetime(1990, 1, 1),
                    phone_number='+22501234567',
                    street='123 Rue Test, Abidjan',
                    jetons=500,
                    date_ouverture=datetime(2025, 1, 1),
                    nombre_jours=30,
                    category_id=2,
                    user_id=2
                )
                db.session.add(client_test)
                print("   - Client user_test créé")
            else:
                print("   - Client user_test existe déjà")
            
            # 6. Créer quelques lots de test
            print("\n6. Création des lots de test...")
            lots = [
                MyWittiLot(
                    id=1,
                    libelle='Carte cadeau 5000 FCFA',
                    slug='carte-cadeau-5000',
                    recompense_image='/static/uploads/gift-card.jpg',
                    jetons=50,
                    stock=100,
                    category_id=1
                ),
                MyWittiLot(
                    id=2,
                    libelle='Paniers cadeaux 10000 FCFA',
                    slug='paniers-cadeaux-10000',
                    recompense_image='/static/uploads/gift-basket.jpg',
                    jetons=100,
                    stock=50,
                    category_id=2
                ),
                MyWittiLot(
                    id=3,
                    libelle='Séance spa 15000 FCFA',
                    slug='seance-spa-15000',
                    recompense_image='/static/uploads/spa.jpg',
                    jetons=150,
                    stock=25,
                    category_id=3
                ),
                MyWittiLot(
                    id=4,
                    libelle='Ticket Brunch 20000 FCFA',
                    slug='ticket-brunch-20000',
                    recompense_image='/static/uploads/brunch.jpg',
                    jetons=200,
                    stock=20,
                    category_id=4
                )
            ]
            
            for lot in lots:
                existing = MyWittiLot.query.get(lot.id)
                if not existing:
                    db.session.add(lot)
                    print(f"   - Lot '{lot.libelle}' créé")
                else:
                    print(f"   - Lot '{lot.libelle}' existe déjà")
            
            # 7. Créer quelques transactions de test
            print("\n7. Création des transactions de test...")
            transactions = [
                MyWittiJetonsTransactions(
                    id=1,
                    client_id=1,
                    montant=100,
                    motif='Épargne mensuelle',
                    date_transaction=datetime.now() - timedelta(days=30)
                ),
                MyWittiJetonsTransactions(
                    id=2,
                    client_id=1,
                    montant=50,
                    motif='Achat carte cadeau',
                    lot_id=1,
                    date_transaction=datetime.now() - timedelta(days=15)
                )
            ]
            
            for transaction in transactions:
                existing = MyWittiJetonsTransactions.query.get(transaction.id)
                if not existing:
                    db.session.add(transaction)
                    print(f"   - Transaction {transaction.id} créée")
                else:
                    print(f"   - Transaction {transaction.id} existe déjà")
            
            # 8. Créer quelques notifications de test
            print("\n8. Création des notifications de test...")
            notifications = [
                MyWittiNotification(
                    id=1,
                    user_id=2,
                    message='Bienvenue dans le programme de fidélité My Witti !',
                    is_read=False,
                    created_at=datetime.now() - timedelta(days=5)
                ),
                MyWittiNotification(
                    id=2,
                    user_id=2,
                    message='Votre commande a été validée. Passez la récupérer en agence.',
                    is_read=False,
                    created_at=datetime.now() - timedelta(days=1)
                )
            ]
            
            for notification in notifications:
                existing = MyWittiNotification.query.get(notification.id)
                if not existing:
                    db.session.add(notification)
                    print(f"   - Notification {notification.id} créée")
                else:
                    print(f"   - Notification {notification.id} existe déjà")
            
            # 9. Créer quelques FAQs de test
            print("\n9. Création des FAQs de test...")
            faqs = [
                MyWittiFAQ(
                    question="Comment puis-je consulter mon solde de jetons ?",
                    answer="Vous pouvez consulter votre solde de jetons sur votre tableau de bord ou dans la section Profil de l'application."
                ),
                MyWittiFAQ(
                    question="Que faire si ma commande est annulée ?",
                    answer="Si votre commande est annulée, vous recevrez une notification expliquant la raison. Contactez l'agence RGK pour plus d'informations."
                )
            ]
            
            for faq in faqs:
                existing = MyWittiFAQ.query.filter_by(question=faq.question).first()
                if not existing:
                    db.session.add(faq)
                    print(f"   - FAQ '{faq.question[:30]}...' créée")
                else:
                    print(f"   - FAQ '{faq.question[:30]}...' existe déjà")
            
            # 10. Créer un sondage de test
            print("\n10. Création du sondage de test...")
            survey = MyWittiSurvey.query.filter_by(title='Satisfaction client').first()
            if not survey:
                survey = MyWittiSurvey(
                    id=1,
                    title='Satisfaction client',
                    description='Sondage pour évaluer la satisfaction de nos clients',
                    is_active=True,
                    created_at=datetime.now()
                )
                db.session.add(survey)
                print("   - Sondage 'Satisfaction client' créé")
                
                # Ajouter des options au sondage
                options = [
                    MyWittiSurveyOption(survey_id=1, option_text='Très satisfait', option_value=5),
                    MyWittiSurveyOption(survey_id=1, option_text='Satisfait', option_value=4),
                    MyWittiSurveyOption(survey_id=1, option_text='Neutre', option_value=3),
                    MyWittiSurveyOption(survey_id=1, option_text='Insatisfait', option_value=2),
                    MyWittiSurveyOption(survey_id=1, option_text='Très insatisfait', option_value=1)
                ]
                
                for option in options:
                    db.session.add(option)
                print("   - Options du sondage créées")
            else:
                print("   - Sondage 'Satisfaction client' existe déjà")
            
            # Valider toutes les modifications
            db.session.commit()
            print("\n✅ Toutes les données de test ont été créées avec succès !")
            
        except Exception as e:
            db.session.rollback()
            print(f"\n❌ Erreur lors de la création des données de test : {str(e)}")
            raise

if __name__ == "__main__":
    create_test_data() 