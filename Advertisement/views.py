# Advertisement/views.py
from flask import Blueprint, current_app, request, jsonify
from flask_restx import Api, Resource, fields
from Models.mywitti_advertisement import MyWittiAdvertisement
from extensions import db
import random

# ---------------------------
# Blueprint + API
# ---------------------------
advertisement_bp = Blueprint('advertisement', __name__, url_prefix='/advertisement')
api = Api(version='1.0', title='Advertisement API', description='API for client advertisement viewing')
api.init_app(advertisement_bp)

# ---------------------------
# Modèles pour documentation
# ---------------------------
advertisement_client_model = api.model('AdvertisementClient', {
    'id': fields.Integer(description='Advertisement ID'),
    'title': fields.String(description='Advertisement title'),
    'description': fields.String(description='Advertisement description'),
    'image_url': fields.String(description='Image URL'),
    'country': fields.String(description='Target country (null for all countries)'),
    'is_active': fields.Boolean(description='Is advertisement active'),
    'created_at': fields.String(description='Creation date'),
    'updated_at': fields.String(description='Last update date')
})

countries_model = api.model('Countries', {
    'countries': fields.List(fields.String, description='Liste des pays disponibles')
})

country_advertisements_model = api.model('CountryAdvertisements', {
    'country': fields.String(description='Pays sélectionné'),
    'advertisements': fields.List(fields.Nested(advertisement_client_model), description='Liste des publicités du pays')
})

country_selection_model = api.model('CountrySelection', {
    'country': fields.String(required=True, description='Pays sélectionné par l\'utilisateur'),
    'customer_code': fields.String(required=True, description='Customer code')
})

# ---------------------------
# Gestion des pays
# ---------------------------
AVAILABLE_COUNTRIES = ["Côte d'Ivoire", "Sénégal", "Burkina Faso"]
from shared_config import set_customer_country, get_user_country

@api.route('/countries')
class AvailableCountries(Resource):
    def get(self):
        try:
            return {"countries": AVAILABLE_COUNTRIES}, 200
        except Exception as e:
            current_app.logger.error(f"Error fetching available countries: {str(e)}")
            return {"error": "Internal server error"}, 500

@api.route('/select-country')
class SelectCountry(Resource):
    def post(self):
        try:
            data = request.get_json()
            country = data.get('country')
            customer_code = data.get('customer_code')

            if not country or not customer_code:
                return {"error": "Pays et customer_code requis"}, 400
            if country not in AVAILABLE_COUNTRIES:
                return {"error": "Pays non valide"}, 400

            set_customer_country(customer_code, country)
            current_app.logger.info(f"Pays sélectionné pour {customer_code}: {country}")

            return {"message": f"Pays sélectionné : {country}", "customer_code": customer_code, "selected_country": country}, 200

        except Exception as e:
            current_app.logger.error(f"Error selecting country: {str(e)}")
            return {"error": "Internal server error"}, 500

@api.route('/get-selected-country/<user_id>')
class GetSelectedCountry(Resource):
    def get(self, user_id):
        try:
            selected_country = get_user_country(user_id)
            if selected_country:
                return {"user_id": user_id, "selected_country": selected_country}, 200
            else:
                return {"user_id": user_id, "selected_country": None, "message": "Aucun pays sélectionné"}, 404
        except Exception as e:
            current_app.logger.error(f"Error getting selected country: {str(e)}")
            return {"error": "Internal server error"}, 500

# ---------------------------
# Publicités aléatoires par pays
# ---------------------------
def get_random_ads_for_country(country):
    ads = MyWittiAdvertisement.query.filter(
        MyWittiAdvertisement.is_active == True,
        db.or_(
            MyWittiAdvertisement.country == country,
            MyWittiAdvertisement.country.is_(None)
        )
    ).all()
    selected = random.sample(ads, 3) if len(ads) > 3 else ads
    current_app.logger.info(f"Ads for {country}: {[ad.to_dict() for ad in selected]}")
    return {"country": country, "advertisements": [ad.to_dict() for ad in selected]}

@api.route('/country/CI/random')
class RandomCountryAdvertisementsCI(Resource):
    def get(self):
        try:
            return get_random_ads_for_country("Côte d'Ivoire"), 200
        except Exception as e:
            current_app.logger.error(f"Error fetching random ads CI: {str(e)}")
            return {"error": "Internal server error"}, 500

@api.route('/country/SE/random')
class RandomCountryAdvertisementsSN(Resource):
    def get(self):
        try:
            return get_random_ads_for_country("Sénégal"), 200
        except Exception as e:
            current_app.logger.error(f"Error fetching random ads SN: {str(e)}")
            return {"error": "Internal server error"}, 500

@api.route('/country/BF/random')
class RandomCountryAdvertisementsBF(Resource):
    def get(self):
        try:
            return get_random_ads_for_country("Burkina Faso"), 200
        except Exception as e:
            current_app.logger.error(f"Error fetching random ads BF: {str(e)}")
            return {"error": "Internal server error"}, 500

# ---------------------------
# Publicités actives
# ---------------------------
def get_active_ads(country=None):
    query = MyWittiAdvertisement.query.filter(MyWittiAdvertisement.is_active == True)
    if country:
        query = query.filter(db.or_(
            MyWittiAdvertisement.country == country,
            MyWittiAdvertisement.country.is_(None)
        ))
    ads = query.order_by(MyWittiAdvertisement.created_at.desc()).limit(3).all()
    current_app.logger.info(f"Active ads for {country or 'all'}: {[ad.to_dict() for ad in ads]}")
    return [ad.to_dict() for ad in ads]

@api.route('/active')
class ActiveAdvertisements(Resource):
    def get(self):
        try:
            return get_active_ads(), 200
        except Exception as e:
            current_app.logger.error(f"Error fetching active ads: {str(e)}")
            return {"error": "Internal server error"}, 500

@api.route('/active/cote-divoire')
class ActiveAdvertisementsCI(Resource):
    def get(self):
        try:
            return get_active_ads("Côte d'Ivoire"), 200
        except Exception as e:
            current_app.logger.error(f"Error fetching active ads CI: {str(e)}")
            return {"error": "Internal server error"}, 500

@api.route('/active/senegal')
class ActiveAdvertisementsSN(Resource):
    def get(self):
        try:
            return get_active_ads("Sénégal"), 200
        except Exception as e:
            current_app.logger.error(f"Error fetching active ads SN: {str(e)}")
            return {"error": "Internal server error"}, 500

@api.route('/active/burkina-faso')
class ActiveAdvertisementsBF(Resource):
    def get(self):
        try:
            return get_active_ads("Burkina Faso"), 200
        except Exception as e:
            current_app.logger.error(f"Error fetching active ads BF: {str(e)}")
            return {"error": "Internal server error"}, 500
