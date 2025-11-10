# Admin/resources/customer.py
from flask import request
from flask_restx import Resource, fields
from flask_jwt_extended import jwt_required, get_jwt_identity
from Models.mywitti_client import MyWittiClient
from Models.mywitti_users import MyWittiUser
from Models.mywitti_comptes import MyWittiCompte
from Models.mywitti_category import MyWittiCategory
from extensions import db
from datetime import datetime

# Import différé pour éviter les problèmes d'import circulaire
def get_api():
    from Admin.views import api
    return api

# Obtenir l'API de manière différée
api = get_api()

# Modèle étendu pour inclure toutes les informations demandées
customer_model = api.model('Customer', {
    'id': fields.Integer(description='Customer ID'),
    'customer_code': fields.String(description='Customer Code'),
    'short_name': fields.String(description='Short Name'),
    'first_name': fields.String(description='First Name'),
    'gender': fields.String(description='Gender'),
    'birth_date': fields.String(description='Birth Date'),
    'phone_number': fields.String(description='Phone Number'),
    'street': fields.String(description='Street'),
    'jetons': fields.Integer(description='Jetons'),
    'category_name': fields.String(description='Nom de la catégorie'),
    'user_email': fields.String(description='Email de l\'utilisateur associé'),
    'numero_compte': fields.String(description='Numéro de compte'),
    'agence': fields.String(description='Agence'),
    'pays_agence': fields.String(description='Pays de l\'agence'),
    'date_ouverture_compte': fields.String(description='Date d\'ouverture du compte'),
    'working_balance': fields.Integer(description='Solde du compte'),
    'libelle_compte': fields.String(description='Libellé du compte'),
    'date_ouverture_client': fields.String(description='Date d\'ouverture client'),
    'nombre_jours': fields.String(description='Nombre de jours'),
    'reliquat_transaction': fields.Integer(description='Reliquat transaction'),
    'reliquat_stabilite': fields.Integer(description='Reliquat stabilité'),
    'jetons_transaction': fields.Integer(description='Jetons transaction'),
    'jetons_stabilite': fields.Integer(description='Jetons stabilité')
})

class CustomerList(Resource):
    @jwt_required()
    @api.marshal_with(customer_model, as_list=True)
    def get(self):
        try:
            # Vérification sécurisée des autorisations admin
            user_id = get_jwt_identity()
            user = MyWittiUser.query.filter_by(user_id=user_id).first()
            if not user or not (user.is_admin or user.is_superuser):
                api.abort(403, "Accès interdit - Droits administrateur requis")
            
            # Récupération sécurisée de tous les clients avec leurs relations
            customers = MyWittiClient.query.all()
            customer_list = []
            
            for customer in customers:
                # Récupérer les informations du compte principal
                compte = MyWittiCompte.query.filter_by(customer_code=customer.customer_code).first()
                
                # Récupérer les informations de l'utilisateur associé
                user_email = "N/A"
                if customer.user:
                    user_email = customer.user.email or "N/A"
                
                # Récupérer le nom de la catégorie
                category_name = "N/A"
                if customer.category:
                    category_name = customer.category.category_name or "N/A"
                
                # Déterminer le pays de l'agence (logique métier)
                pays_agence = "Côte d'Ivoire"  # Par défaut
                if compte and compte.agence:
                    agence_lower = compte.agence.lower()
                    if 'abidjan' in agence_lower:
                        pays_agence = "Côte d'Ivoire"
                    elif 'ouagadougou' in agence_lower or 'burkina' in agence_lower:
                        pays_agence = "Burkina Faso"
                    elif 'bamako' in agence_lower or 'mali' in agence_lower:
                        pays_agence = "Mali"
                    elif 'dakar' in agence_lower or 'senegal' in agence_lower:
                        pays_agence = "Sénégal"
                    elif 'lome' in agence_lower or 'togo' in agence_lower:
                        pays_agence = "Togo"
                    elif 'niamey' in agence_lower or 'niger' in agence_lower:
                        pays_agence = "Niger"
                    elif 'conakry' in agence_lower or 'guinee' in agence_lower:
                        pays_agence = "Guinée"
                    elif 'bissau' in agence_lower or 'guinee-bissau' in agence_lower:
                        pays_agence = "Guinée-Bissau"
                    elif 'bangui' in agence_lower or 'centrafrique' in agence_lower:
                        pays_agence = "République Centrafricaine"
                    elif 'njamena' in agence_lower or 'tchad' in agence_lower:
                        pays_agence = "Tchad"
                    elif 'yaounde' in agence_lower or 'cameroun' in agence_lower:
                        pays_agence = "Cameroun"
                    elif 'libreville' in agence_lower or 'gabon' in agence_lower:
                        pays_agence = "Gabon"
                    elif 'brazzaville' in agence_lower or 'congo' in agence_lower:
                        pays_agence = "Congo"
                    elif 'kinshasa' in agence_lower or 'rdc' in agence_lower:
                        pays_agence = "République Démocratique du Congo"
                    elif 'malabo' in agence_lower or 'guinee-equatoriale' in agence_lower:
                        pays_agence = "Guinée Équatoriale"
                    elif 'sao-tome' in agence_lower or 'sao tome' in agence_lower:
                        pays_agence = "São Tomé-et-Principe"
                    elif 'djibouti' in agence_lower:
                        pays_agence = "Djibouti"
                    elif 'comores' in agence_lower or 'moroni' in agence_lower:
                        pays_agence = "Comores"
                    elif 'madagascar' in agence_lower or 'antananarivo' in agence_lower:
                        pays_agence = "Madagascar"
                    elif 'maurice' in agence_lower or 'port-louis' in agence_lower:
                        pays_agence = "Maurice"
                    elif 'seychelles' in agence_lower or 'victoria' in agence_lower:
                        pays_agence = "Seychelles"
                    elif 'france' in agence_lower or 'paris' in agence_lower:
                        pays_agence = "France"
                    elif 'belgique' in agence_lower or 'bruxelles' in agence_lower:
                        pays_agence = "Belgique"
                    elif 'suisse' in agence_lower or 'geneve' in agence_lower:
                        pays_agence = "Suisse"
                    elif 'canada' in agence_lower or 'montreal' in agence_lower:
                        pays_agence = "Canada"
                    elif 'etats-unis' in agence_lower or 'new-york' in agence_lower:
                        pays_agence = "États-Unis"
                
                customer_data = {
                    'id': customer.id,
                    'customer_code': customer.customer_code or "N/A",
                    'short_name': customer.short_name or "N/A",
                    'first_name': customer.first_name or "N/A",
                    'gender': customer.gender or "N/A",
                    'birth_date': customer.birth_date.strftime('%Y-%m-%d') if customer.birth_date else "N/A",
                    'phone_number': customer.phone_number or "N/A",
                    'street': customer.street or "N/A",
                    'jetons': customer.jetons or 0,
                    'category_name': category_name,
                    'user_email': user_email,
                    'numero_compte': compte.numero_compte if compte else "N/A",
                    'agence': compte.agence if compte else "N/A",
                    'pays_agence': pays_agence,
                    'date_ouverture_compte': compte.date_ouverture_compte.strftime('%Y-%m-%d') if compte and compte.date_ouverture_compte else "N/A",
                    'working_balance': compte.working_balance if compte else 0,
                    'libelle_compte': compte.libelle if compte else "N/A",
                    'date_ouverture_client': customer.date_ouverture or "N/A",
                    'nombre_jours': customer.nombre_jours or "N/A",
                    'reliquat_transaction': customer.reliquat_transaction or 0,
                    'reliquat_stabilite': customer.reliquat_stabilite or 0,
                    'jetons_transaction': customer.jetons_transaction or 0,
                    'jetons_stabilite': customer.jetons_stabilite or 0
                }
                
                customer_list.append(customer_data)
            
            return customer_list, 200
            
        except Exception as e:
            api.abort(500, f"Erreur lors de la récupération des clients: {str(e)}")

    @jwt_required()
    @api.marshal_with(customer_model)
    def get(self, customer_id):
        try:
            # Vérification sécurisée des autorisations admin
            user_id = get_jwt_identity()
            user = MyWittiUser.query.filter_by(user_id=user_id).first()
            if not user or not (user.is_admin or user.is_superuser):
                api.abort(403, "Accès interdit - Droits administrateur requis")
            
            # Récupération sécurisée du client spécifique
            customer = MyWittiClient.query.get(customer_id)
            if not customer:
                api.abort(404, "Client non trouvé")
            
            # Récupérer les informations du compte
            compte = MyWittiCompte.query.filter_by(customer_code=customer.customer_code).first()
            
            # Récupérer les informations de l'utilisateur associé
            user_email = "N/A"
            if customer.user:
                user_email = customer.user.email or "N/A"
            
            # Récupérer le nom de la catégorie
            category_name = "N/A"
            if customer.category:
                category_name = customer.category.category_name or "N/A"
            
            # Déterminer le pays de l'agence (même logique que ci-dessus)
            pays_agence = "Côte d'Ivoire"  # Par défaut
            if compte and compte.agence:
                agence_lower = compte.agence.lower()
                # Logique de détermination du pays (simplifiée pour l'exemple)
                if any(pays in agence_lower for pays in ['abidjan', 'yamoussoukro', 'bouake']):
                    pays_agence = "Côte d'Ivoire"
                elif any(pays in agence_lower for pays in ['ouagadougou', 'bobo']):
                    pays_agence = "Burkina Faso"
                elif any(pays in agence_lower for pays in ['bamako', 'segou']):
                    pays_agence = "Mali"
                # ... autres pays selon les besoins
            
            customer_data = {
                'id': customer.id,
                'customer_code': customer.customer_code or "N/A",
                'short_name': customer.short_name or "N/A",
                'first_name': customer.first_name or "N/A",
                'gender': customer.gender or "N/A",
                'birth_date': customer.birth_date.strftime('%Y-%m-%d') if customer.birth_date else "N/A",
                'phone_number': customer.phone_number or "N/A",
                'street': customer.street or "N/A",
                'jetons': customer.jetons or 0,
                'category_name': category_name,
                'user_email': user_email,
                'numero_compte': compte.numero_compte if compte else "N/A",
                'agence': compte.agence if compte else "N/A",
                'pays_agence': pays_agence,
                'date_ouverture_compte': compte.date_ouverture_compte.strftime('%Y-%m-%d') if compte and compte.date_ouverture_compte else "N/A",
                'working_balance': compte.working_balance if compte else 0,
                'libelle_compte': compte.libelle if compte else "N/A",
                'date_ouverture_client': customer.date_ouverture or "N/A",
                'nombre_jours': customer.nombre_jours or "N/A",
                'reliquat_transaction': customer.reliquat_transaction or 0,
                'reliquat_stabilite': customer.reliquat_stabilite or 0,
                'jetons_transaction': customer.jetons_transaction or 0,
                'jetons_stabilite': customer.jetons_stabilite or 0
            }
            
            return customer_data, 200
            
        except Exception as e:
            api.abort(500, f"Erreur lors de la récupération du client: {str(e)}") 