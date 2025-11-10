# Lot/views.py
from flask import Blueprint, current_app, request, jsonify, url_for
from flask_restx import Api, Resource, fields
from flask_jwt_extended import jwt_required, get_jwt_identity
from Models.mywitti_users import MyWittiUser
from Models.mywitti_client import MyWittiClient
from Models.mywitti_lots import MyWittiLot
from Models.mywitti_lots_favoris import MyWittiLotsFavoris
from Models.mywitti_lots_claims import MyWittiLotsClaims
from Models.mywitti_notification import MyWittiNotification
from Models.mywitti_category import MyWittiCategory
from extensions import db
from datetime import datetime
from sqlalchemy.exc import IntegrityError
import uuid

lot_bp = Blueprint('lot', __name__, url_prefix='/lot')
api = Api(lot_bp, version='1.0', title='Lot API', description='API for lot operations')

# ======================================
# Modèles pour API
# ======================================
reward_model = {
    'id': fields.Integer,
    'title': fields.String,
    'tokens_required': fields.Integer,
    'image_url': fields.String,
    'category': fields.String,
    'quantity_available': fields.Integer
}

favorites_response_model = api.model('FavoritesResponse', {
    'count': fields.Integer(description='Number of favorites'),
    'items': fields.List(fields.Nested(reward_model), description='List of favorite rewards')
})

cart_item_model = api.model('CartItem', {
    'id': fields.Integer(description='Item ID'),
    'title': fields.String(description='Item title'),
    'quantity': fields.Integer(description='Quantity'),
    'tokens_required_per_item': fields.Integer(description='Tokens required per item'),
    'total_tokens': fields.Integer(description='Total tokens for this item'),
    'image_url': fields.String(description='Item image URL'),
    'transaction_id': fields.String(description='Transaction ID')
})

cart_response_model = api.model('CartResponse', {
    'jetons_disponibles': fields.Integer(description='Available tokens'),
    'jetons_requis': fields.Integer(description='Required tokens'),
    'achat_possible': fields.Boolean(description='Purchase possible'),
    'transactions': fields.List(fields.Nested(cart_item_model), description='Cart items'),
    'notifications': fields.List(fields.String, description='Messages')
})

# ======================================
# Panier en mémoire
# ======================================
cart_quantities = {}

# ======================================
# Routes récompenses disponibles
# ======================================
@api.route('/rewards')
class AvailableRewards(Resource):
    @jwt_required()
    @api.marshal_list_with(api.model('AvailableReward', reward_model))
    def get(self):
        try:
            rewards = MyWittiLot.query.filter(MyWittiLot.stock > 0).all()
            available_rewards = []

            for reward in rewards:
                quantity_available = reward.stock if reward.stock and reward.stock > 0 else 0
                available_rewards.append({
                    "id": reward.id,
                    "title": reward.libelle or "Sans titre",
                    "tokens_required": reward.jetons or 0,
                    "image_url": url_for('serve_image', filename=reward.recompense_image, _external=True)
                                 if reward.recompense_image else "",
                    "category": reward.category.category_name if reward.category else "Sans catégorie",
                    "quantity_available": quantity_available
                })

            return available_rewards, 200
        except Exception as e:
            current_app.logger.error(f"Error fetching rewards: {str(e)}")
            return {"error": "Internal server error"}, 500

# ======================================
# Favoris
# ======================================
@api.route('/favorites', methods=['POST'])
class ToggleFavorite(Resource):
    @jwt_required()
    def post(self):
        try:
            user_id = get_jwt_identity()
            user = MyWittiUser.query.filter_by(user_id=user_id).first()
            if not user:
                return {"message": "Utilisateur non trouvé"}, 404

            client = MyWittiClient.query.filter_by(user_id=user.id).first()
            if not client:
                return {"message": "Client non trouvé"}, 404

            data = request.get_json()
            reward_id = data.get("reward_id")
            if not reward_id:
                return {"message": "L'ID de la récompense est requis"}, 400

            reward = MyWittiLot.query.get(reward_id)
            if not reward:
                return {"message": "Récompense non trouvée"}, 404

            favorite = MyWittiLotsFavoris.query.filter_by(client_id=client.id, lot_id=reward_id).first()
            if favorite:
                db.session.delete(favorite)
                db.session.commit()
                return {"msg": "Récompense retirée des favoris"}
            else:
                new_favorite = MyWittiLotsFavoris(
                    client_id=client.id,
                    lot_id=reward_id,
                    date_ajout=datetime.utcnow()
                )
                db.session.add(new_favorite)
                db.session.commit()
                return {"msg": "Récompense ajoutée aux favoris"}
        except IntegrityError:
            db.session.rollback()
            return {"message": "Cette récompense est déjà dans vos favoris"}, 400
        except Exception as e:
            current_app.logger.error(f"Error toggling favorite: {str(e)}")
            db.session.rollback()
            return {"error": "Internal server error"}, 500

@api.route('/favorites', methods=['GET'])
class GetFavorites(Resource):
    @jwt_required()
    @api.marshal_with(favorites_response_model)
    def get(self):
        try:
            user_id = get_jwt_identity()
            user = MyWittiUser.query.filter_by(user_id=user_id).first()
            if not user:
                return {"message": "Utilisateur non trouvé"}, 404

            client = MyWittiClient.query.filter_by(user_id=user.id).first()
            if not client:
                return {"message": "Client non trouvé"}, 404

            favorites = MyWittiLotsFavoris.query.filter_by(client_id=client.id).all()
            favorite_rewards = []

            for fav in favorites:
                reward = MyWittiLot.query.get(fav.lot_id)
                if reward and (reward.stock is None or reward.stock > 0):
                    favorite_rewards.append({
                        "id": reward.id,
                        "title": reward.libelle or "Sans titre",
                        "tokens_required": reward.jetons or 0,
                        "category": reward.category.category_name if reward.category else "Sans catégorie",
                        "image_url": url_for('serve_image', filename=reward.recompense_image, _external=True) if reward.recompense_image else ""
                    })

            return {"count": len(favorite_rewards), "items": favorite_rewards}
        except Exception as e:
            current_app.logger.error(f"Error fetching favorites: {str(e)}")
            return {"error": "Internal server error"}, 500

# ======================================
# Panier
# ======================================
@api.route('/cart', methods=['POST'])
class AddToCart(Resource):
    @jwt_required()
    def post(self):
        try:
            user_id = get_jwt_identity()
            user = MyWittiUser.query.filter_by(user_id=user_id).first()
            if not user:
                return {"message": "Utilisateur non trouvé"}, 404

            data = request.get_json()
            reward_id = data.get('reward_id')
            quantity = data.get('quantity', 1)
            if not reward_id or quantity <= 0:
                return {"message": "ID de récompense et quantité valides requis"}, 400

            reward = MyWittiLot.query.get(reward_id)
            if not reward:
                return {"message": "Récompense non trouvée"}, 404

            if not reward.stock or reward.stock < quantity:
                return {"message": "Quantité insuffisante en stock"}, 400

            customer = MyWittiClient.query.filter_by(user_id=user.id).first()
            if not customer:
                return {"message": "Client non trouvé"}, 404

            total_tokens_required = (reward.jetons or 0) * quantity
            eligible = customer.jetons >= total_tokens_required
            if not eligible:
                return {
                    "msg": "Jetons insuffisants pour ajouter cette récompense au panier",
                    "eligible": False,
                    "tokens_required": total_tokens_required,
                    "tokens_available": customer.jetons
                }, 400

            cart_item = MyWittiLotsClaims.query.filter_by(
                client_id=customer.id,
                lot_id=reward_id,
                statut='cart'
            ).first()

            if not cart_quantities.get(customer.id):
                cart_quantities[customer.id] = {}

            if cart_item:
                cart_quantities[customer.id][cart_item.id] = cart_quantities[customer.id].get(cart_item.id, 1) + quantity
            else:
                cart_item = MyWittiLotsClaims(
                    client_id=customer.id,
                    lot_id=reward_id,
                    statut='cart',
                    date_reclamation=datetime.utcnow()
                )
                db.session.add(cart_item)
                db.session.commit()
                cart_quantities[customer.id][cart_item.id] = quantity

            db.session.commit()

            return {
                "msg": f"{reward.libelle} ajoutée au panier",
                "eligible": True,
                "quantity": cart_quantities[customer.id][cart_item.id],
                "total_tokens": cart_quantities[customer.id][cart_item.id] * (reward.jetons or 0),
                "tokens_available": customer.jetons
            }, 200
        except Exception as e:
            current_app.logger.error(f"Error adding to cart: {str(e)}")
            db.session.rollback()
            return {"error": "Internal server error"}, 500

@api.route('/cart', methods=['GET'])
class ViewCart(Resource):
    @jwt_required()
    @api.marshal_with(cart_response_model)
    def get(self):
        try:
            user_id = get_jwt_identity()
            user = MyWittiUser.query.filter_by(user_id=user_id).first()
            if not user:
                return {"message": "Utilisateur non trouvé"}, 404

            customer = MyWittiClient.query.filter_by(user_id=user.id).first()
            if not customer:
                return {"message": "Client non trouvé"}, 404

            cart_items = MyWittiLotsClaims.query.filter_by(client_id=customer.id, statut='cart').all()
            transactions = []
            total_required = 0
            jetons_disponibles = customer.jetons if customer else 0

            for item in cart_items:
                reward = MyWittiLot.query.get(item.lot_id)
                if reward:
                    if customer.id not in cart_quantities:
                        cart_quantities[customer.id] = {}
                    if item.id not in cart_quantities[customer.id]:
                        cart_quantities[customer.id][item.id] = 1
                    qty = cart_quantities[customer.id][item.id]

                    transactions.append({
                        "id": item.id,
                        "title": reward.libelle or "Sans titre",
                        "quantity": qty,
                        "tokens_required_per_item": reward.jetons or 0,
                        "total_tokens": (reward.jetons or 0) * qty,
                        "image_url": url_for('serve_image', filename=reward.recompense_image, _external=True) if reward.recompense_image else "",
                        "transaction_id": str(uuid.uuid4())
                    })
                    total_required += (reward.jetons or 0) * qty

            achat_possible = jetons_disponibles >= total_required
            notifications = ["Vérifiez vos jetons disponibles avant l'achat."] if not achat_possible else []

            return {
                "jetons_disponibles": jetons_disponibles,
                "jetons_requis": total_required,
                "achat_possible": achat_possible,
                "transactions": transactions,
                "notifications": notifications
            }
        except Exception as e:
            current_app.logger.error(f"Error viewing cart: {str(e)}")
            return {"error": "Internal server error"}, 500


@api.route('/place-order', methods=['POST'])
class PlaceOrder(Resource):
    @jwt_required()
    def post(self):
        try:
            user_id = get_jwt_identity()
            user = MyWittiUser.query.filter_by(user_id=user_id).first()
            if not user:
                return {"message": "Utilisateur non trouvé"}, 404

            customer = MyWittiClient.query.filter_by(user_id=user.id).first()
            if not customer:
                return {"message": "Client non trouvé"}, 404

            cart_items = MyWittiLotsClaims.query.filter_by(client_id=customer.id, statut='cart').all()
            if not cart_items:
                return {"message": "Panier vide"}, 400

            total_tokens_required = 0
            for item in cart_items:
                reward = MyWittiLot.query.get(item.lot_id)
                if not reward:
                    return {"message": f"Récompense {item.lot_id} introuvable"}, 404
                if reward.stock is not None and reward.stock < cart_quantities.get(customer.id, {}).get(item.id, 1):
                    return {"message": f"Stock insuffisant pour {reward.libelle}"}, 400
                total_tokens_required += (reward.jetons or 0) * cart_quantities.get(customer.id, {}).get(item.id, 1)

            if customer.jetons < total_tokens_required:
                return {"message": "Jetons insuffisants pour cette commande"}, 400

            # Débiter les jetons et passer la commande
            for item in cart_items:
                reward = MyWittiLot.query.get(item.lot_id)
                quantity = cart_quantities.get(customer.id, {}).get(item.id, 1)

                # Mettre à jour le stock
                if reward.stock is not None:
                    reward.stock -= quantity

                # Marquer l'item comme commandé
                item.statut = 'ordered'
                item.date_reclamation = datetime.utcnow()

            customer.jetons -= total_tokens_required
            db.session.commit()

            # Nettoyer le panier en mémoire
            cart_quantities[customer.id] = {}

            return {"msg": "Commande passée avec succès", "total_tokens_used": total_tokens_required}, 200

        except Exception as e:
            current_app.logger.error(f"Error placing order: {str(e)}")
            db.session.rollback()
            return {"error": "Internal server error"}, 500

# ======================================
# Update quantity in cart
# ======================================
@api.route('/cart/update_quantity', methods=['POST'])
class UpdateQuantity(Resource):
    @jwt_required()
    def post(self):
        try:
            user_id = get_jwt_identity()
            user = MyWittiUser.query.filter_by(user_id=user_id).first()
            if not user:
                return {"message": "Utilisateur non trouvé"}, 404

            data = request.get_json()
            item_id = data.get("item_id")
            quantity = data.get("quantity", 1)
            if not item_id or quantity <= 0:
                return {"message": "ID de l'article et quantité valides requis"}, 400

            customer = MyWittiClient.query.filter_by(user_id=user.id).first()
            if not customer:
                return {"message": "Client non trouvé"}, 404

            cart_item = MyWittiLotsClaims.query.filter_by(id=item_id, client_id=customer.id, statut='cart').first()
            if not cart_item:
                return {"message": "Article non trouvé dans le panier"}, 404

            reward = MyWittiLot.query.get(cart_item.lot_id)
            if not reward or (reward.stock and quantity > reward.stock):
                return {"message": "Quantité invalide ou stock insuffisant"}, 400

            cart_quantities.setdefault(customer.id, {})[cart_item.id] = quantity
            db.session.commit()

            return {"msg": "Quantité mise à jour", "quantity": quantity}, 200
        except Exception as e:
            current_app.logger.error(f"Error updating cart quantity: {str(e)}")
            db.session.rollback()
            return {"error": "Internal server error"}, 500

# ======================================
# Routes par catégorie (avec tri décroissant)
# ======================================
def build_category_response(category_ids, default_name):
    CATEGORY_PRIORITY = {
        "firstclass": 4,
        "executive+": 3,
        "executive": 2,
        "ecopremium": 1
    }

    rewards = MyWittiLot.query.filter(
        MyWittiLot.stock > 0,
        MyWittiLot.category_id.in_(category_ids)
    ).all()

    rewards_sorted = sorted(
        rewards,
        key=lambda r: CATEGORY_PRIORITY.get(
            r.category.category_name.lower().replace(" ", ""), 0
        ),
        reverse=True
    )

    response = []
    for r in rewards_sorted:
        response.append({
            "id": r.id,
            "title": r.libelle or "Sans titre",
            "tokens_required": r.jetons or 0,
            "image_url": url_for('serve_image', filename=r.recompense_image, _external=True) if r.recompense_image else "",
            "category": r.category.category_name if r.category else default_name,
            "quantity_available": r.stock
        })
    return response


@api.route('/rewards/eco-premium')
class RewardsEcoPremium(Resource):
    @jwt_required()
    @api.marshal_list_with(api.model('EcoPremiumReward', reward_model))
    def get(self):
        try:
            return build_category_response([1], "ECO PREMIUM"), 200
        except Exception as e:
            current_app.logger.error(f"Erreur Eco Premium: {str(e)}")
            return {"error": "Erreur interne du serveur"}, 500

@api.route('/rewards/executive')
class RewardsExecutive(Resource):
    @jwt_required()
    @api.marshal_list_with(api.model('ExecutiveReward', reward_model))
    def get(self):
        try:
            # Executive voit Executive + Eco Premium
            return build_category_response([2, 1], "EXECUTIVE"), 200
        except Exception as e:
            current_app.logger.error(f"Erreur Executive: {str(e)}")
            return {"error": "Erreur interne du serveur"}, 500

@api.route('/rewards/executive-plus')
class RewardsExecutivePlus(Resource):
    @jwt_required()
    @api.marshal_list_with(api.model('ExecutivePlusReward', reward_model))
    def get(self):
        try:
            # Executive+ voit Executive+, Executive, Eco Premium
            return build_category_response([3, 2, 1], "EXECUTIVE+"), 200
        except Exception as e:
            current_app.logger.error(f"Erreur Executive Plus: {str(e)}")
            return {"error": "Erreur interne du serveur"}, 500

@api.route('/rewards/first-class')
class RewardsFirst(Resource):
    @jwt_required()
    @api.marshal_list_with(api.model('FirstReward', reward_model))
    def get(self):
        try:
            # First voit tout
            return build_category_response([4, 3, 2, 1], "FIRST"), 200
        except Exception as e:
            current_app.logger.error(f"Erreur First: {str(e)}")
            return {"error": "Erreur interne du serveur"}, 500
