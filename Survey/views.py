from flask import Blueprint, current_app, request
from flask_restx import Api, Resource, fields
from flask_jwt_extended import jwt_required, get_jwt_identity
from Models.mywitti_users import MyWittiUser
from Models.mywitti_client import MyWittiClient
from Models.mywitti_survey import MyWittiSurvey, MyWittiSurveyOption, MyWittiSurveyResponse
from extensions import db
from datetime import datetime

survey_bp = Blueprint('survey', __name__)
api = Api(survey_bp, version='1.0', title='Survey API', description='API for survey operations')

# Modèles de réponse
survey_model = api.model('Survey', {
    'id': fields.Integer(description='Survey ID'),
    'title': fields.String(description='Survey title'),
    'description': fields.String(description='Survey description'),
    'is_active': fields.Boolean(description='Is survey active'),
    'created_at': fields.String(description='Creation date')
})

survey_option_model = api.model('SurveyOption', {
    'id': fields.Integer(description='Option ID'),
    'option_text': fields.String(description='Option text'),
    'option_value': fields.Integer(description='Option value')
})

survey_response_model = api.model('SurveyResponse', {
    'id': fields.Integer(description='Response ID'),
    'survey_id': fields.Integer(description='Survey ID'),
    'option_id': fields.Integer(description='Selected option ID'),
    'submitted_at': fields.String(description='Submission date')
})

surveys_response_model = api.model('SurveysResponse', {
    'msg': fields.String(description='Success message'),
    'surveys': fields.List(fields.Nested(survey_model), description='List of surveys')
})

survey_detail_response_model = api.model('SurveyDetailResponse', {
    'msg': fields.String(description='Success message'),
    'survey': fields.Nested(survey_model, description='Survey details'),
    'options': fields.List(fields.Nested(survey_option_model), description='Survey options')
})

@survey_bp.before_request
def log_routes():
    for rule in current_app.url_map.iter_rules():
        current_app.logger.info(f"Route: {rule.endpoint} -> {rule}")

@api.route('/surveys')
class SurveyList(Resource):
    @jwt_required()
    @api.marshal_with(surveys_response_model)
    def get(self):
        try:
            # Récupération sécurisée des sondages actifs
            surveys = MyWittiSurvey.query.filter_by(is_active=True).all()
            surveys_data = [{
                'id': survey.id,
                'title': survey.title or "Sans titre",
                'description': survey.description or "Aucune description",
                'is_active': survey.is_active,
                'created_at': survey.created_at.strftime('%Y-%m-%d %H:%M:%S') if survey.created_at else "Unknown"
            } for survey in surveys]

            return {
                'msg': 'Sondages récupérés avec succès',
                'surveys': surveys_data
            }, 200
        except Exception as e:
            current_app.logger.error(f"Error fetching surveys: {str(e)}")
            return {"error": "Internal server error"}, 500

@api.route('/surveys/<int:survey_id>')
class SurveyDetail(Resource):
    @jwt_required()
    @api.marshal_with(survey_detail_response_model)
    def get(self, survey_id):
        try:
            # Récupération sécurisée du sondage
            survey = MyWittiSurvey.query.get_or_404(survey_id)
            options = MyWittiSurveyOption.query.filter_by(survey_id=survey_id).all()

            survey_data = {
                'id': survey.id,
                'title': survey.title or "Sans titre",
                'description': survey.description or "Aucune description",
                'is_active': survey.is_active,
                'created_at': survey.created_at.strftime('%Y-%m-%d %H:%M:%S') if survey.created_at else "Unknown"
            }

            options_data = [{
                'id': option.id,
                'option_text': option.option_text or "Option sans texte",
                'option_value': option.option_value or 0
            } for option in options]

            return {
                'msg': 'Détails du sondage récupérés avec succès',
                'survey': survey_data,
                'options': options_data
            }, 200
        except Exception as e:
            current_app.logger.error(f"Error fetching survey details: {str(e)}")
            return {"error": "Internal server error"}, 500

@api.route('/surveys/<int:survey_id>/respond')
class SurveyResponse(Resource):
    @jwt_required()
    def post(self, survey_id):
        try:
            # Récupération sécurisée de l'utilisateur
            user_identifiant = get_jwt_identity()
            current_app.logger.info(f"Tentative de réponse au sondage {survey_id} par {user_identifiant}")

            # Vérification que l'utilisateur existe et est actif
            user = MyWittiUser.query.filter_by(user_id=user_identifiant).first()
            if not user or not user.is_active:
                current_app.logger.error(f"Utilisateur {user_identifiant} non trouvé ou inactif")
                return {"message": "Utilisateur non trouvé ou inactif"}, 404

            # Vérification que le client existe
            customer = MyWittiClient.query.filter_by(customer_code=user_identifiant).first()
            if not customer:
                current_app.logger.error(f"Client non trouvé pour identifiant {user_identifiant}")
                return {"message": "Client non trouvé"}, 404

            # Vérification que le sondage existe et est actif
            survey = MyWittiSurvey.query.filter_by(id=survey_id, is_active=True).first()
            if not survey:
                return {"message": "Sondage non trouvé ou inactif"}, 404

            # Récupération et validation des données de la requête
            data = request.get_json()
            if not data:
                return {"message": "Données JSON requises"}, 400

            option_id = data.get('option_id')

            if not option_id:
                return {"message": "option_id est requis"}, 400

            # Validation que l'option_id est un entier
            try:
                option_id = int(option_id)
            except (ValueError, TypeError):
                return {"message": "option_id doit être un nombre entier"}, 400

            # Vérification que l'option existe pour ce sondage
            option = MyWittiSurveyOption.query.filter_by(id=option_id, survey_id=survey_id).first()
            if not option:
                return {"message": "Option invalide pour ce sondage"}, 400

            # Vérification que l'utilisateur n'a pas déjà répondu à ce sondage
            existing_response = MyWittiSurveyResponse.query.filter_by(
                survey_id=survey_id,
                user_id=user.id
            ).first()

            if existing_response:
                current_app.logger.warning(f"Utilisateur {user_identifiant} a déjà répondu au sondage {survey_id}")
                return {"message": "Vous avez déjà répondu à ce sondage"}, 400

            # Création sécurisée de la réponse
            response = MyWittiSurveyResponse(
                survey_id=survey_id,
                user_id=user.id,
                customer_id=customer.id,
                option_id=option_id,
                submitted_at=datetime.utcnow()
            )

            db.session.add(response)
            db.session.commit()

            current_app.logger.info(f"Réponse enregistrée avec succès pour le sondage {survey_id} par {user_identifiant}")
            return {"message": "Réponse enregistrée avec succès"}, 201

        except Exception as e:
            current_app.logger.error(f"Error submitting survey response: {str(e)}")
            db.session.rollback()
            return {"error": "Internal server error"}, 500