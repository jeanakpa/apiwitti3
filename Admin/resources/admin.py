# admin/resources/admin.py (corrigé)
from flask import request
from flask_restx import Resource, fields
from flask_jwt_extended import jwt_required, get_jwt_identity
from Models.mywitti_users import MyWittiUser
from Admin.views import api
from extensions import db
from werkzeug.security import generate_password_hash
from datetime import datetime

admin_model = api.model('Admin', {
    'id': fields.Integer(description='Admin ID'),
    'first_name': fields.String(description='First Name'),
    'last_name': fields.String(description='Last Name'),
    'email': fields.String(description='Email'),
    'user_id': fields.String(description='User ID'),
    'is_admin': fields.Boolean(description='Is Admin'),
    'is_superuser': fields.Boolean(description='Is Superuser'),
    'is_active': fields.Boolean(description='Is Active'),
    'created_at': fields.String(description='Creation date')
})

admin_input_model = api.model('AdminInput', {
    'first_name': fields.String(required=True, description='First Name'),
    'last_name': fields.String(required=True, description='Last Name'),
    'email': fields.String(required=True, description='Email'),
    'user_id': fields.String(required=True, description='User ID'),
    'password': fields.String(required=True, description='Password'),
    'is_admin': fields.Boolean(description='Is Admin'),
    'is_superuser': fields.Boolean(description='Is Superuser')
})

admin_response_model = api.model('AdminResponse', {
    'msg': fields.String(description='Success message'),
    'admin_id': fields.Integer(description='ID of the created admin')
})

class AdminList(Resource):
    @jwt_required()
    @api.marshal_with(admin_model, as_list=True)
    def get(self):
        try:
            # Vérification sécurisée des autorisations super admin
            user_id = get_jwt_identity()
            user = MyWittiUser.query.filter_by(user_id=user_id).first()
            if not user or not user.is_superuser:
                api.abort(403, "Accès interdit - Droits super administrateur requis")
            
            # Récupération sécurisée de tous les admins
            admins = MyWittiUser.query.filter(
                (MyWittiUser.is_admin == True) | (MyWittiUser.is_superuser == True)
            ).all()
            
            return [{
                'id': admin.id,
                'first_name': admin.first_name or "N/A",
                'last_name': admin.last_name or "N/A",
                'email': admin.email or "N/A",
                'user_id': admin.user_id or "N/A",
                'is_admin': admin.is_admin or False,
                'is_superuser': admin.is_superuser or False,
                'is_active': admin.is_active or False,
                'created_at': admin.created_at.strftime('%Y-%m-%d %H:%M:%S') if admin.created_at else "Unknown"
            } for admin in admins]
        except Exception as e:
            api.abort(500, f"Erreur lors de la récupération des admins: {str(e)}")

    @jwt_required()
    @api.expect(admin_input_model)
    @api.marshal_with(admin_response_model, code=201)
    def post(self):
        try:
            # Vérification sécurisée des autorisations super admin
            user_id = get_jwt_identity()
            user = MyWittiUser.query.filter_by(user_id=user_id).first()
            if not user or not user.is_superuser:
                api.abort(403, "Seuls les super admins peuvent créer des administrateurs")

            # Récupération et validation des données
            data = request.get_json()
            if not data:
                api.abort(400, "Données JSON requises")

            # Validation des champs obligatoires
            required_fields = ['first_name', 'last_name', 'email', 'user_id', 'password']
            for field in required_fields:
                if not data.get(field):
                    api.abort(400, f"Le champ {field} est requis")

            # Validation du format email
            email = data['email']
            if '@' not in email or '.' not in email:
                api.abort(400, "Format d'email invalide")

            # Validation de la longueur du mot de passe
            password = data['password']
            if len(password) < 6:
                api.abort(400, "Le mot de passe doit contenir au moins 6 caractères")

            # Vérification de l'unicité de l'email et user_id
            if MyWittiUser.query.filter_by(email=email).first():
                api.abort(400, "Cet email est déjà utilisé")
            
            if MyWittiUser.query.filter_by(user_id=data['user_id']).first():
                api.abort(400, "Cet identifiant utilisateur est déjà utilisé")

            # Création sécurisée du nouvel admin
            new_admin = MyWittiUser(
                first_name=data['first_name'],
                last_name=data['last_name'],
                email=email,
                user_id=data['user_id'],
                password_hash=generate_password_hash(password),
                is_admin=data.get('is_admin', False),
                is_superuser=data.get('is_superuser', False),
                is_active=True,
                created_at=datetime.utcnow()
            )

            db.session.add(new_admin)
            db.session.commit()

            return {
                'msg': 'Administrateur créé avec succès',
                'admin_id': new_admin.id
            }, 201

        except Exception as e:
            db.session.rollback()
            api.abort(500, f"Erreur lors de la création de l'administrateur: {str(e)}")

    @jwt_required()
    @api.expect(admin_input_model)
    @api.marshal_with(admin_response_model, code=200)
    def put(self):
        try:
            # Vérification sécurisée des autorisations super admin
            user_id = get_jwt_identity()
            user = MyWittiUser.query.filter_by(user_id=user_id).first()
            if not user or not user.is_superuser:
                api.abort(403, "Seuls les super admins peuvent modifier des administrateurs")

            # Récupération et validation des données
            data = request.get_json()
            if not data:
                api.abort(400, "Données JSON requises")

            admin_id = data.get('id')
            if not admin_id:
                api.abort(400, "ID de l'administrateur requis pour la modification")

            # Récupération sécurisée de l'admin
            admin = MyWittiUser.query.get(admin_id)
            if not admin:
                api.abort(404, "Administrateur non trouvé")

            # Validation des champs obligatoires
            required_fields = ['first_name', 'last_name', 'email', 'user_id']
            for field in required_fields:
                if not data.get(field):
                    api.abort(400, f"Le champ {field} est requis")

            # Validation du format email
            email = data['email']
            if '@' not in email or '.' not in email:
                api.abort(400, "Format d'email invalide")

            # Vérification de l'unicité de l'email et user_id (excluant l'admin actuel)
            existing_email = MyWittiUser.query.filter_by(email=email).first()
            if existing_email and existing_email.id != admin_id:
                api.abort(400, "Cet email est déjà utilisé par un autre utilisateur")
            
            existing_user_id = MyWittiUser.query.filter_by(user_id=data['user_id']).first()
            if existing_user_id and existing_user_id.id != admin_id:
                api.abort(400, "Cet identifiant utilisateur est déjà utilisé par un autre utilisateur")

            # Mise à jour sécurisée de l'admin
            admin.first_name = data['first_name']
            admin.last_name = data['last_name']
            admin.email = email
            admin.user_id = data['user_id']
            admin.is_admin = data.get('is_admin', admin.is_admin)
            admin.is_superuser = data.get('is_superuser', admin.is_superuser)

            # Mise à jour du mot de passe si fourni
            if data.get('password'):
                password = data['password']
                if len(password) < 6:
                    api.abort(400, "Le mot de passe doit contenir au moins 6 caractères")
                admin.password_hash = generate_password_hash(password)

            admin.updated_at = datetime.utcnow()
            db.session.commit()

            return {
                'msg': 'Administrateur mis à jour avec succès',
                'admin_id': admin.id
            }, 200

        except Exception as e:
            db.session.rollback()
            api.abort(500, f"Erreur lors de la mise à jour de l'administrateur: {str(e)}")

    @jwt_required()
    @api.marshal_with(admin_response_model, code=200)
    def delete(self, admin_id):
        try:
            # Vérification sécurisée des autorisations super admin
            user_id = get_jwt_identity()
            user = MyWittiUser.query.filter_by(user_id=user_id).first()
            if not user or not user.is_superuser:
                api.abort(403, "Seuls les super admins peuvent supprimer des administrateurs")

            # Empêcher la suppression de soi-même
            if int(admin_id) == user.id:
                api.abort(400, "Vous ne pouvez pas supprimer votre propre compte")

            # Récupération sécurisée de l'admin
            admin = MyWittiUser.query.get(admin_id)
            if not admin:
                api.abort(404, "Administrateur non trouvé")

            # Vérification si c'est le dernier super admin
            if admin.is_superuser:
                super_admin_count = MyWittiUser.query.filter_by(is_superuser=True).count()
                if super_admin_count <= 1:
                    api.abort(400, "Impossible de supprimer le dernier super administrateur")

            # Suppression sécurisée de l'admin
            db.session.delete(admin)
            db.session.commit()

            return {
                'msg': 'Administrateur supprimé avec succès',
                'admin_id': int(admin_id)
            }, 200

        except Exception as e:
            db.session.rollback()
            api.abort(500, f"Erreur lors de la suppression de l'administrateur: {str(e)}")