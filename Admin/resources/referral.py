# Admin/resources/referral.py
from flask import request
from flask_restx import Resource, fields
from flask_jwt_extended import jwt_required, get_jwt_identity
from Models.mywitti_referral import MyWittiReferral
from Models.mywitti_users import MyWittiUser
from extensions import db

# Définir les modèles sans dépendre de l'api
ns = None  # L'espace de noms sera défini dans views.py

referral_model = {
    'id': fields.Integer(description='ID du parrainage'),
    'referrer_id': fields.Integer(description='ID de l\'utilisateur parrain'),
    'referrer_email': fields.String(description='Email de l\'utilisateur parrain'),
    'referred_email': fields.String(description='Email de l\'ami invité'),
    'referral_link': fields.String(description='Lien de parrainage'),
    'status': fields.String(description='Statut du parrainage'),
    'created_at': fields.String(description='Date de création')
}

update_status_model = {
    'status': fields.String(required=True, description='Nouveau statut (pending, accepted, rewarded)')
}

class ReferralManagementResource(Resource):
    @jwt_required()
    def get(self):
        identifiant = get_jwt_identity()
        admin = MyWittiUser.query.filter_by(user_id=identifiant).first()
        if not admin:
            return {'message': 'Utilisateur non trouvé'}, 404
        if not (admin.is_admin or admin.is_superuser):
            return {'message': 'Accès réservé aux administrateurs'}, 403
        
        try:
            referrals = MyWittiReferral.query.all()
            referral_data = []
            
            for referral in referrals:
                # Vérifier que la relation existe
                referrer_email = 'N/A'
                if referral.referrer:
                    referrer_email = referral.referrer.email
                
                referral_data.append({
                    'id': referral.id,
                    'referrer_id': referral.referrer_id,
                    'referrer_email': referrer_email,
                    'referred_email': referral.referred_email,
                    'referral_link': f"http://127.0.0.1:5000/accounts/refer/{referral.referral_code}",
                    'status': referral.status,
                    'created_at': referral.created_at.isoformat() if referral.created_at else None
                })
            
            return referral_data, 200
            
        except Exception as e:
            print(f"Erreur lors de la récupération des parrainages: {str(e)}")
            return [], 200

    @jwt_required()
    def put(self, referral_id):
        identifiant = get_jwt_identity()
        admin = MyWittiUser.query.filter_by(user_id=identifiant).first()
        if not admin:
            return {'message': 'Utilisateur non trouvé'}, 404
        if not (admin.is_admin or admin.is_superuser):
            return {'message': 'Accès réservé aux administrateurs'}, 403
        referral = MyWittiReferral.query.get(referral_id)
        if not referral:
            return {'message': 'Parrainage non trouvé'}, 404
        data = request.get_json()
        new_status = data.get('status')
        if new_status not in ['En cours', 'Accepté', 'Récompensé']:
            return {'message': 'Statut invalide'}, 400
        referral.status = new_status
        db.session.commit()
        return {'message': 'Statut mis à jour avec succès'}, 200

    @jwt_required()
    def delete(self, referral_id):
        identifiant = get_jwt_identity()
        admin = MyWittiUser.query.filter_by(user_id=identifiant).first()
        if not admin:
            return {'message': 'Utilisateur non trouvé'}, 404
        if not (admin.is_admin or admin.is_superuser):
            return {'message': 'Accès réservé aux administrateurs'}, 403
        referral = MyWittiReferral.query.get(referral_id)
        if not referral:
            return {'message': 'Parrainage non trouvé'}, 404
        db.session.delete(referral)
        db.session.commit()
        return {'message': 'Parrainage supprimé avec succès'}, 200