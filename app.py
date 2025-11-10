# app.py
import logging
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import Flask, request, send_from_directory, current_app
from flask_cors import CORS
from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request
from Models.page_visit import PageVisit
from config import config
from extensions import db, ma, jwt, migrate
from Models.token_blacklist import TokenBlacklist
from Models.mywitti_users import MyWittiUser

# Dossier contenant les images
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
IMAGE_FOLDER = os.path.join(BASE_DIR, 'Image_2')

def create_app(config_name=None):
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')
        if config_name not in config:
            config_name = 'development'

    app = Flask(__name__)
    app.config.from_object(config[config_name])

    # Configuration dossier images
    app.config['IMAGE_FOLDER'] = IMAGE_FOLDER

    # CORS global
    CORS(app, resources={r"/*": {"origins": "*"}})

    # Logging
    logging.basicConfig(
        level=getattr(logging, app.config.get('LOG_LEVEL', 'INFO')),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    app.logger.setLevel(getattr(logging, app.config.get('LOG_LEVEL', 'INFO')))

    # Initialisation extensions
    db.init_app(app)
    ma.init_app(app)
    jwt.init_app(app)
    migrate.init_app(app, db)

    # Import blueprints
    from Account.views import accounts_bp
    from Customer.views import customer_bp
    from Lot.views import lot_bp
    from Admin.views import admin_bp
    from Faq.views import faq_bp
    from Support.views import support_bp
    from Survey.views import survey_bp
    from Advertisement.views import advertisement_bp

    app.register_blueprint(accounts_bp, url_prefix='/accounts')
    app.register_blueprint(customer_bp, url_prefix='/customer')
    app.register_blueprint(lot_bp, url_prefix='/lot')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(faq_bp, url_prefix='/faq')
    app.register_blueprint(support_bp, url_prefix='/support')
    app.register_blueprint(survey_bp, url_prefix='/survey')
    app.register_blueprint(advertisement_bp, url_prefix='/advertisement')

    # Route globale pour servir les images
    @app.route('/images/<path:filename>')
    def serve_image(filename):
        # Log pour debug
        current_app.logger.info(f"Demande image: {filename}")
        full_path = os.path.join(app.config['IMAGE_FOLDER'], filename)
        if not os.path.isfile(full_path):
            current_app.logger.warning(f"Fichier introuvable: {full_path}")
            return {"error": "Image non trouvée"}, 404
        return send_from_directory(app.config['IMAGE_FOLDER'], filename)

    # Vérification token blacklist
    @jwt.token_in_blocklist_loader
    def check_if_token_is_revoked(jwt_header, jwt_payload):
        jti = jwt_payload['jti']
        token = db.session.query(TokenBlacklist).filter_by(jti=jti).first()
        return token is not None

    # Tracking des pages
    @app.before_request
    def track_page_visit():
        if request.method == 'OPTIONS':
            return

        path = request.path
        user_id = None

        try:
            if 'Authorization' in request.headers:
                verify_jwt_in_request()
                identifiant = get_jwt_identity()
                if identifiant:
                    user = MyWittiUser.query.filter_by(user_id=identifiant).first()
                    user_id = user.id if user else None
        except Exception as e:
            app.logger.warning(f"Erreur récupération identité : {e}")

        try:
            page_visit = PageVisit(path=path, user_id=user_id)
            db.session.add(page_visit)
            db.session.commit()
        except Exception as e:
            app.logger.error(f"Erreur enregistrement visite : {e}")
            db.session.rollback()

    return app


app = create_app()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
