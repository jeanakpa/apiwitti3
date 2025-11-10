import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
# application.py (copie de app.py pour éviter le conflit avec gunicorn.app)
import logging
from flask import Flask, request, send_from_directory
from flask_cors import CORS
from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request
from Models.page_visit import PageVisit
from config import config
from extensions import db, ma, jwt, migrate

# Importation des modèles
from Models.mywitti_survey import MyWittiSurvey, MyWittiSurveyOption, MyWittiSurveyResponse
from Models.mywitti_faq import MyWittiFAQ
from Models.mywitti_resultat import MyWittiResultatCriteria, MyWittiResultatTotal, MyWittiResultatPoint, MyWittiClientRecompense
from Models.token_blacklist import TokenBlacklist
from Models.mywitti_support_request import MyWittiSupportRequest
from Models.mywitti_users import MyWittiUser
from Models.mywitti_user_type import MyWittiUserType
from Models.mywitti_client import MyWittiClient
from Models.mywitti_comptes import MyWittiCompte
from Models.mywitti_lots import MyWittiLot
from Models.mywitti_lots_favoris import MyWittiLotsFavoris
from Models.mywitti_lots_claims import MyWittiLotsClaims
from Models.mywitti_jetons_transactions import MyWittiJetonsTransactions
from Models.mywitti_client_palier_history import MyWittiClientPalierHistory
from Models.mywitti_client_jetons_daily import MyWittiClientJetonsDaily
from Models.mywitti_category import MyWittiCategory
from Models.mywitti_referral import MyWittiReferral
from Models.mywitti_faq import MyWittiFAQ
from Models.mywitti_support_request import MyWittiSupportRequest
from Models.mywitti_advertisement import MyWittiAdvertisement

@jwt.token_in_blocklist_loader
def check_if_token_is_revoked(jwt_header, jwt_payload):
    jti = jwt_payload['jti']
    token = db.session.query(TokenBlacklist).filter_by(jti=jti).first()
    return token is not None

def create_app(config_name=None):
    # Déterminer la configuration à utiliser - forcer le développement par défaut
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')
        # S'assurer qu'on utilise bien la config de développement
        if config_name not in config:
            config_name = 'development'
    
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # Configuration CORS
    CORS(app, origins=app.config.get('CORS_ORIGINS', '*'))
    
    # Configuration du logging
    logging.basicConfig(
        level=getattr(logging, app.config.get('LOG_LEVEL', 'INFO')),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    app.logger.setLevel(getattr(logging, app.config.get('LOG_LEVEL', 'INFO')))
    
    if app.config.get('DEBUG'):
        app.logger.info("Application starting in DEBUG mode")
    else:
        app.logger.info("Application starting in PRODUCTION mode")

    # Initialisation des extensions
    db.init_app(app)
    ma.init_app(app)
    jwt.init_app(app)
    migrate.init_app(app, db)

    # Importation des blueprints après l'initialisation
    from Account.views import accounts_bp
    from Customer.views import customer_bp
    from Lot.views import lot_bp
    from Admin.views import admin_bp
    from Faq.views import faq_bp
    from Support.views import support_bp
    from Survey.views import survey_bp
    from Advertisement.views import advertisement_bp

    # Enregistrement des blueprints
    app.register_blueprint(accounts_bp, url_prefix='/accounts')
    app.register_blueprint(customer_bp, url_prefix='/customer')
    app.register_blueprint(lot_bp, url_prefix='/lot')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(faq_bp, url_prefix='/faq')
    app.register_blueprint(support_bp, url_prefix='/support')
    app.register_blueprint(survey_bp, url_prefix='/survey')
    app.register_blueprint(advertisement_bp, url_prefix='/advertisement')

    # Route pour servir les images
    @app.route('/static/uploads/<path:filename>')
    def serve_uploaded_file(filename):
        return send_from_directory('static/uploads', filename)

    # Gestionnaire d'erreurs global
    @app.errorhandler(404)
    def not_found(error):
        return {"error": "Endpoint non trouvé"}, 404

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return {"error": "Erreur interne du serveur"}, 500

    # Enregistrer les visites de pages
    @app.before_request
    def track_page_visit():
        # Ignorer les requêtes OPTIONS (CORS preflight)
        if request.method == 'OPTIONS':
            return

        path = request.path
        user_id = None
        
        try:
            # Vérifier si un jeton est présent avant de récupérer l'identité
            if 'Authorization' in request.headers:
                verify_jwt_in_request()  # Vérifie le jeton sans exiger @jwt_required
                identifiant = get_jwt_identity()
                if identifiant:
                    user = MyWittiUser.query.filter_by(user_id=identifiant).first()
                    user_id = user.id if user else None
        except Exception as e:
            app.logger.warning(f"Erreur lors de la récupération de l'identité : {e}")
        
        try:
            page_visit = PageVisit(path=path, user_id=user_id)
            db.session.add(page_visit)
            db.session.commit()
        except Exception as e:
            app.logger.error(f"Erreur lors de l'enregistrement de la visite : {e}")
            db.session.rollback()

    return app


app = create_app()

if __name__ == '__main__':
    app.run(debug=app.config.get('DEBUG', False)) 