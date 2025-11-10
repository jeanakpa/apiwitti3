# admin/resources/customer.py (version mise à jour)
from flask import request
from flask_restx import Resource, fields
from flask_jwt_extended import jwt_required, get_jwt_identity
from Models.mywitti_client import MyWittiClient
from Models.mywitti_users import MyWittiUser
# Import différé pour éviter les problèmes d'import circulaire
from Admin.views import api
from extensions import db
from datetime import datetime

customer_model = api.model('Customer', {
    'id': fields.Integer(description='Customer ID'),
    'customer_code': fields.String(description='Customer Code'),
    'short_name': fields.String(description='Short Name'),
    'first_name': fields.String(description='First Name'),
    'gender': fields.String(description='Gender'),
    'birth_date': fields.String(description='Birth Date'),
    'phone_number': fields.String(description='Phone Number'),
    'street': fields.String(description='Street'),
    'total': fields.Integer(description='Total'),
    'jetons': fields.Integer(description='Jetons'),
    'numero_compte': fields.String(description='Numéro de compte'),
    'agence': fields.String(description='Agence'),
    'date_ouverture_compte': fields.String(description='Date d\'ouverture du compte'),
    'working_balance': fields.Integer(description='Solde du compte'),
    'category_name': fields.String(description='Nom de la catégorie'),
    'user_email': fields.String(description='Email de l\'utilisateur associé')
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

customer_response_model = api.model('CustomerResponse', {
    'msg': fields.String(description='Message de succès'),
    'customer_id': fields.Integer(description='ID du client créé')
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
                
                customer_data = {
                    'id': customer.id,
                    'customer_code': customer.customer_code or "N/A",
                    'short_name': customer.short_name or "N/A",
                    'first_name': customer.first_name or "N/A",
                    'gender': customer.gender or "N/A",
                    'birth_date': str(customer.birth_date) if customer.birth_date else "N/A",
                    'phone_number': customer.phone_number or "N/A",
                    'street': customer.street or "N/A",
                    'total': 0,  # Champ fictif ou calculé si besoin
                    'jetons': customer.jetons or 0,
                    'numero_compte': compte.numero_compte if compte else "N/A",
                    'agence': compte.agence if compte else "N/A",
                    'date_ouverture_compte': str(compte.date_ouverture_compte) if compte and compte.date_ouverture_compte else "N/A",
                    'working_balance': compte.working_balance if compte else 0,
                    'category_name': category_name,
                    'user_email': user_email
                }
                customer_list.append(customer_data)
            
            return customer_list
        except Exception as e:
            api.abort(500, f"Erreur interne: {str(e)}")

    @jwt_required()
    @api.expect(customer_input_model)
    @api.marshal_with(customer_response_model, code=201)
    def post(self):
        try:
            # Vérification sécurisée des autorisations admin
            user_id = get_jwt_identity()
            user = MyWittiUser.query.filter_by(user_id=user_id).first()
            if not user or not (user.is_admin or user.is_superuser):
                api.abort(403, "Accès interdit - Droits administrateur requis")

            # Récupération et validation des données
            data = request.get_json()
            if not data:
                api.abort(400, "Données JSON requises")

            # Validation des champs obligatoires
            required_fields = ['customer_code', 'short_name', 'first_name', 'gender', 'birth_date', 'street']
            for field in required_fields:
                if not data.get(field):
                    api.abort(400, f"Le champ {field} est requis.")

            # Validation du format de la date de naissance
            try:
                datetime.strptime(data['birth_date'], '%Y-%m-%d')
            except ValueError:
                api.abort(400, "Format de date invalide. Utilisez YYYY-MM-DD")

            # Validation du genre
            if data['gender'] not in ['M', 'F']:
                api.abort(400, "Le genre doit être 'M' ou 'F'")

            # Vérification de l'unicité du code client
            if MyWittiClient.query.filter_by(customer_code=data['customer_code']).first():
                api.abort(400, "Ce code client existe déjà.")

            # Validation du numéro de téléphone (optionnel mais formaté si présent)
            phone_number = data.get('phone_number')
            if phone_number and len(phone_number) < 8:
                api.abort(400, "Le numéro de téléphone doit contenir au moins 8 chiffres")

            # Création sécurisée du nouveau client
            new_customer = MyWittiClient(
                customer_code=data['customer_code'],
                short_name=data['short_name'],
                first_name=data['first_name'],
                gender=data['gender'],
                birth_date=data['birth_date'],
                phone_number=phone_number,
                street=data['street'],
                user_id=data.get('user_id'),
                category_id=data.get('category_id'),
                jetons=data.get('jetons', 0)
            )

            db.session.add(new_customer)
            db.session.commit()

            return {
                'msg': 'Client créé avec succès',
                'customer_id': new_customer.id
            }, 201

        except Exception as e:
            db.session.rollback()
            api.abort(500, f"Erreur lors de la création du client: {str(e)}")

    @jwt_required()
    @api.expect(customer_input_model)
    @api.marshal_with(customer_response_model, code=200)
    def put(self):
        try:
            # Vérification sécurisée des autorisations admin
            user_id = get_jwt_identity()
            user = MyWittiUser.query.filter_by(user_id=user_id).first()
            if not user or not (user.is_admin or user.is_superuser):
                api.abort(403, "Accès interdit - Droits administrateur requis")

            # Récupération et validation des données
            data = request.get_json()
            if not data:
                api.abort(400, "Données JSON requises")

            customer_id = data.get('id')
            if not customer_id:
                api.abort(400, "ID du client requis pour la modification")

            # Récupération sécurisée du client
            customer = MyWittiClient.query.get(customer_id)
            if not customer:
                api.abort(404, "Client non trouvé")

            # Validation des champs obligatoires
            required_fields = ['customer_code', 'short_name', 'first_name', 'gender', 'birth_date', 'street']
            for field in required_fields:
                if not data.get(field):
                    api.abort(400, f"Le champ {field} est requis.")

            # Validation du format de la date de naissance
            try:
                datetime.strptime(data['birth_date'], '%Y-%m-%d')
            except ValueError:
                api.abort(400, "Format de date invalide. Utilisez YYYY-MM-DD")

            # Validation du genre
            if data['gender'] not in ['M', 'F']:
                api.abort(400, "Le genre doit être 'M' ou 'F'")

            # Vérification de l'unicité du code client (excluant le client actuel)
            existing_customer = MyWittiClient.query.filter_by(customer_code=data['customer_code']).first()
            if existing_customer and existing_customer.id != customer_id:
                api.abort(400, "Ce code client est déjà utilisé par un autre client.")

            # Validation du numéro de téléphone
            phone_number = data.get('phone_number')
            if phone_number and len(phone_number) < 8:
                api.abort(400, "Le numéro de téléphone doit contenir au moins 8 chiffres")

            # Mise à jour sécurisée du client
            customer.customer_code = data['customer_code']
            customer.short_name = data['short_name']
            customer.first_name = data['first_name']
            customer.gender = data['gender']
            customer.birth_date = data['birth_date']
            customer.phone_number = phone_number
            customer.street = data['street']
            customer.jetons = data.get('jetons', customer.jetons)

            db.session.commit()

            return {
                'msg': 'Client mis à jour avec succès',
                'customer_id': customer.id
            }, 200

        except Exception as e:
            db.session.rollback()
            api.abort(500, f"Erreur lors de la mise à jour du client: {str(e)}")

    @jwt_required()
    @api.marshal_with(customer_response_model, code=200)
    def delete(self, customer_id):
        try:
            # Vérification sécurisée des autorisations admin
            user_id = get_jwt_identity()
            user = MyWittiUser.query.filter_by(user_id=user_id).first()
            if not user or not (user.is_admin or user.is_superuser):
                api.abort(403, "Accès interdit - Droits administrateur requis")

            # Récupération sécurisée du client
            customer = MyWittiClient.query.get(customer_id)
            if not customer:
                api.abort(404, "Client non trouvé")

            db.session.delete(customer)
            db.session.commit()

            return {
                'msg': 'Client supprimé avec succès',
                'customer_id': customer_id
            }, 200

        except Exception as e:
            db.session.rollback()
            api.abort(500, f"Erreur lors de la suppression du client: {str(e)}") 