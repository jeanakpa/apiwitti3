from flask import Blueprint, current_app, request
from flask_restx import Api, Resource, fields
from flask_jwt_extended import jwt_required, get_jwt_identity
from Models.mywitti_users import MyWittiUser
from Models.mywitti_support_request import MyWittiSupportRequest
from extensions import db
from datetime import datetime

support_bp = Blueprint('support', __name__)
api = Api(support_bp, version='1.0', title='Support API', description='API for support operations')

# Modèles de réponse
support_contact_model = api.model('SupportContact', {
    'phone': fields.String(description='Support phone number'),
    'whatsapp': fields.String(description='Support WhatsApp number'),
    'email': fields.String(description='Support email'),
    'default_message': fields.String(description='Default WhatsApp message')
})

support_request_model = api.model('SupportRequest', {
    'id': fields.Integer(description='Request ID'),
    'subject': fields.String(description='Request subject'),
    'description': fields.String(description='Request description'),
    'request_type': fields.String(description='Request type'),
    'status': fields.String(description='Request status'),
    'created_at': fields.String(description='Creation date')
})

support_request_input_model = api.model('SupportRequestInput', {
    'subject': fields.String(required=True, description='Request subject'),
    'description': fields.String(required=True, description='Request description'),
    'request_type': fields.String(required=True, description='Request type (Reclamation, Assistance, Autre)')
})

support_requests_response_model = api.model('SupportRequestsResponse', {
    'msg': fields.String(description='Success message'),
    'requests': fields.List(fields.Nested(support_request_model), description='List of support requests')
})

@api.route('/requests')
class GetSupportRequests(Resource):
    @jwt_required()
    @api.marshal_with(support_requests_response_model)
    def get(self):
        try:
            identifiant = get_jwt_identity()
            user = db.session.query(MyWittiUser).filter_by(user_id=identifiant).first()
            
            if not user:
                return {"message": "User not found"}, 404
            
            requests = MyWittiSupportRequest.query.filter_by(user_id=user.id).order_by(MyWittiSupportRequest.created_at.desc()).all()
            return {
                "msg": "Liste des demandes récupérée avec succès",
                "requests": [req.to_dict() for req in requests]
            }, 200
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Erreur lors de la récupération des demandes: {str(e)}")
            return {"message": f"Erreur serveur: {str(e)}"}, 500



@api.route('/contact')
class SupportContact(Resource):
    @jwt_required()
    @api.marshal_with(support_contact_model)
    def get(self):
        try:
            identifiant = get_jwt_identity()
            user = db.session.query(MyWittiUser).filter_by(user_id=identifiant).first()
            
            if not user:
                current_app.logger.warning(f"Support contact failed: User with identifiant {identifiant} not found")
                return {"message": "User not found"}, 404
            
            # Récupérer les informations de contact du support depuis la configuration
            support_info = {
                'phone': current_app.config.get('SUPPORT_PHONE', '+2250710922213'),
                'whatsapp': current_app.config.get('SUPPORT_WHATSAPP', '+2250710922213'),
                'email': current_app.config.get('SUPPORT_EMAIL', 'misterjohn0798@gmail.com'),
                'default_message': current_app.config.get('WHATSAPP_DEFAULT_MESSAGE', 'Bonjour, j\'ai besoin d\'aide avec l\'application.')
            }
            
            current_app.logger.info(f"Support contact information retrieved for user {identifiant}")
            return support_info, 200
            
        except Exception as e:
            current_app.logger.error(f"Error retrieving support contact: {str(e)}")
            return {"error": str(e)}, 500

@api.route('/request', methods=['POST'])
class CreateSupportRequest(Resource):
    @jwt_required()
    @api.expect(support_request_input_model)
    def post(self):
        try:
            identifiant = get_jwt_identity()
            user = db.session.query(MyWittiUser).filter_by(user_id=identifiant).first()
            
            if not user:
                current_app.logger.warning(f"Support request failed: User with identifiant {identifiant} not found")
                return {"message": "User not found"}, 404
            
            data = request.get_json()
            
            # Validation des champs requis
            required_fields = ['subject', 'description', 'request_type']
            for field in required_fields:
                if not data.get(field):
                    return {"message": f"Le champ {field} est requis"}, 400
            
            # Validation du type de demande
            valid_types = ['Reclamation', 'Assistance', 'Autre']
            if data['request_type'] not in valid_types:
                return {"message": f"Type de demande invalide. Types autorisés: {', '.join(valid_types)}"}, 400
            
            # Créer la demande de support
            support_request = MyWittiSupportRequest(
                user_id=user.id,
                subject=data['subject'],
                description=data['description'],
                request_type=data['request_type'],
                status='Pending',
                created_at=datetime.utcnow()
            )
            
            db.session.add(support_request)
            db.session.commit()
            
            current_app.logger.info(f"Support request {support_request.id} submitted by user {identifiant}")
            return {
                "message": "Demande de support créée avec succès",
                "request_id": support_request.id
            }, 201
            
        except Exception as e:
            current_app.logger.error(f"Error creating support request: {str(e)}")
            db.session.rollback()
            return {"error": str(e)}, 500