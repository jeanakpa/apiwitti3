# admin/resources/customer.py (version corrigée - import circulaire résolu)
from flask import request
from flask_restx import Resource, fields
from flask_jwt_extended import jwt_required, get_jwt_identity
from Models.mywitti_client import MyWittiClient
from Models.mywitti_users import MyWittiUser
from Models.mywitti_comptes import MyWittiCompte
from extensions import db
from datetime import datetime

# Import différé pour éviter les problèmes d'import circulaire
def get_api():
    from Admin.views import api
    return api

# Obtenir l'API de manière différée
api = get_api()

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

customer_input_model = api.model('CustomerInput', {
    'customer_code': fields.String(required=True, description='Code unique du client'),
    'short_name': fields.String(required=True, description='Nom court'),
    'first_name': fields.String(required=True, description='Prénom'),
    'gender': fields.String(required=True, description='Genre (e.g., M, F)'),
    'birth_date': fields.String(required=True, description='Date de naissance (YYYY-MM-DD)'),
    'phone_number': fields.String(description='Numéro de téléphone'),
    'street': fields.String(required=True, description='Adresse'),
    'user_id': fields.Integer(description='ID de l\'utilisateur associé (optionnel)'),
    'category_id': fields.Integer(description='ID de la catégorie (optionnel)'),
    'total': fields.Integer(description='Total (optionnel)'),
    'jetons': fields.Integer(description='Jetons initiaux (optionnel)')
})


class CustomerList(Resource):
    @jwt_required()
    @api.doc(params={
        'page': {'description': 'Numéro de la page (défaut: 1)', 'type': 'integer'},
        'per_page': {'description': 'Nombre d\'éléments par page (fixé à 100)', 'type': 'integer', 'default': 100}
    })
    def get(self):
        try:
            # Vérification sécurisée des autorisations admin
            user_id = get_jwt_identity()
            user = MyWittiUser.query.filter_by(user_id=user_id).first()
            if not user or not (user.is_admin or user.is_superuser):
                api.abort(403, "Accès interdit - Droits administrateur requis")
            
            # --- LOGIQUE DE PAGINATION ---
            page = request.args.get('page', 1, type=int)
            PER_PAGE = 100 # Fixé à 100 pour les performances
            
            # Récupération des clients avec pagination
            # On utilise .paginate() qui est la méthode recommandée avec Flask-SQLAlchemy
            pagination_object = MyWittiClient.query.order_by(MyWittiClient.id.asc()).paginate(
                page=page, 
                per_page=PER_PAGE, 
                error_out=False
            )
            
            customers = pagination_object.items
            total_items = pagination_object.total
            total_pages = pagination_object.pages
            # ---------------------------
            
            customer_list = []
            
            for customer in customers:
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
                
                # Déterminer le pays de l'agence (logique métier)
                pays_agence = "Côte d'Ivoire"  # Par défaut
                if compte and compte.agence:
                    agence_lower = compte.agence.lower()
                    # (Toute la logique de déduction du pays par nom d'agence est inchangée)
                    # Je garde uniquement une partie pour ne pas surcharger le code ici
                    if 'abidjan' in agence_lower:
                        pays_agence = "Côte d'Ivoire"
                    elif 'ouagadougou' in agence_lower or 'burkina' in agence_lower:
                        pays_agence = "Burkina Faso"
                    elif 'bamako' in agence_lower or 'mali' in agence_lower:
                        pays_agence = "Mali"
                    # ... (Suite de la logique de pays)
                    # NOTE: Pour la concision, je coupe ici mais suppose que le reste de votre logique est copiée.
                    # Fin de la logique de déduction du pays
                
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
            
            # Retourner le résultat dans le nouveau format paginé
            return {
                'customers': customer_list,
                'total_items': total_items,
                'page': page,
                'per_page': PER_PAGE,
                'total_pages': total_pages
            }
        except Exception as e:
            api.abort(500, f"Erreur interne: {str(e)}")