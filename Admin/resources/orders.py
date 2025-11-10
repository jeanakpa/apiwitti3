# admin/resources/orders.py
from flask_restx import Resource, fields
from flask_jwt_extended import jwt_required, get_jwt_identity
from Models.mywitti_users import MyWittiUser
from Models.mywitti_lots import MyWittiLot
from Models.mywitti_lots_favoris import MyWittiLotsFavoris
from Models.mywitti_lots_claims import MyWittiLotsClaims
from Models.mywitti_client import MyWittiClient
from Models.mywitti_notification import MyWittiNotification
from Models.mywitti_comptes import MyWittiCompte
from extensions import db
from Admin.views import api
from datetime import datetime

# Modèles pour les réponses
order_model = api.model('Order', {
    'id': fields.String(description='ID de la commande'),
    'user_id': fields.Integer(description='ID de l\'utilisateur'),
    'customer_id': fields.Integer(description='ID du client'),
    'amount': fields.Float(description='Montant de la commande'),
    'status': fields.String(description='Statut de la commande'),
    'contact': fields.String(description='Contact'),
    'date': fields.String(description='Date de la commande'),
    'items': fields.List(fields.Raw, description='Articles de la commande')
})

orders_response_model = api.model('OrdersResponse', {
    'msg': fields.String(description='Message de réponse'),
    'orders': fields.List(fields.Nested(order_model), description='Liste des commandes')
})

order_update_response_model = api.model('OrderUpdateResponse', {
    'msg': fields.String(description='Message de réponse'),
    'status': fields.String(description='Nouveau statut de la commande')
})

class AdminOrders(Resource):
    @jwt_required()
    @api.marshal_with(orders_response_model)
    def get(self):
        try:
            # Vérification sécurisée des autorisations admin
            admin_identifiant = get_jwt_identity()
            admin = MyWittiUser.query.filter_by(user_id=admin_identifiant).first()
            if not admin or not (admin.is_admin or admin.is_superuser):
                return {"msg": "Utilisateur non autorisé - Droits administrateur requis"}, 403

            # Récupération sécurisée des commandes avec tri par statut et date
            orders = MyWittiLotsClaims.query.filter(
                MyWittiLotsClaims.statut.in_(['pending', 'validated', 'cancelled'])
            ).order_by(
                db.case(
                    (MyWittiLotsClaims.statut == 'pending', 1),
                    (MyWittiLotsClaims.statut == 'validated', 2),
                    (MyWittiLotsClaims.statut == 'cancelled', 3),
                    else_=4
                ),
                MyWittiLotsClaims.date_reclamation.asc()
            ).all()

            orders_data = []
            for order in orders:
                # Récupération sécurisée des détails de la récompense
                reward = MyWittiLot.query.get(order.lot_id)
                if reward:
                    items_data = [{
                        'reward_id': reward.id,
                        'libelle': reward.libelle or "Sans titre",
                        'quantity': 1,  # Simplifié - supposant 1 par commande
                        'jeton': reward.jetons or 0
                    }]
                    orders_data.append({
                        'id': str(order.id),
                        'user_id': order.client_id,
                        'customer_id': order.client_id,
                        'amount': float(reward.jetons or 0),
                        'status': order.statut or "pending",
                        'contact': "N/A",
                        'date': order.date_reclamation.strftime('%Y-%m-%d %H:%M:%S') if order.date_reclamation else "Unknown",
                        'items': items_data
                    })
            return {'msg': 'Commandes récupérées avec succès', 'orders': orders_data}
        except Exception as e:
            return {"msg": f"Erreur lors de la récupération des commandes: {str(e)}"}, 500

class AdminOrderDetail(Resource):
    @jwt_required()
    @api.marshal_with(order_model)
    def get(self, order_id):
        try:
            # Vérification sécurisée des autorisations admin
            admin_identifiant = get_jwt_identity()
            admin = MyWittiUser.query.filter_by(user_id=admin_identifiant).first()
            if not admin or not (admin.is_admin or admin.is_superuser):
                return {"msg": "Utilisateur non autorisé - Droits administrateur requis"}, 403

            # Récupération sécurisée de la commande
            order = MyWittiLotsClaims.query.get(order_id)
            if not order:
                return {"msg": "Commande non trouvée"}, 404

            # Récupération sécurisée des détails de la récompense
            reward = MyWittiLot.query.get(order.lot_id)
            if not reward:
                return {"msg": "Récompense non trouvée pour cette commande"}, 404

            items_data = [{
                'reward_id': reward.id,
                'libelle': reward.libelle or "Sans titre",
                'quantity': 1,  # Simplifié - supposant 1 par commande
                'jeton': reward.jetons or 0
            }]

            order_data = {
                'id': str(order.id),
                'user_id': order.client_id,
                'customer_id': order.client_id,
                'amount': float(reward.jetons or 0),
                'status': order.statut or "pending",
                'contact': "N/A",
                'date': order.date_reclamation.strftime('%Y-%m-%d %H:%M:%S') if order.date_reclamation else "Unknown",
                'items': items_data
            }
            return order_data
        except Exception as e:
            return {"msg": f"Erreur lors de la récupération des détails: {str(e)}"}, 500

class ValidateOrder(Resource):
    @jwt_required()
    @api.marshal_with(order_update_response_model)
    def put(self, order_id):
        try:
            # Vérification sécurisée des autorisations super admin
            admin_identifiant = get_jwt_identity()
            admin = MyWittiUser.query.filter_by(user_id=admin_identifiant).first()
            if not admin or not admin.is_superuser:
                return {"msg": "Seuls les super admins peuvent valider les commandes"}, 403

            # Récupération sécurisée de la commande
            order = MyWittiLotsClaims.query.get(order_id)
            if not order:
                return {"msg": "Commande non trouvée"}, 404
            if order.statut == 'cancelled':
                return {"msg": "Une commande annulée ne peut pas être validée"}, 400
            if order.statut == 'validated':
                return {"msg": "La commande est déjà validée"}, 400

            # Récupération sécurisée de la récompense
            reward = MyWittiLot.query.get(order.lot_id)
            if not reward:
                return {"msg": "Récompense non trouvée"}, 404

            # Vérification sécurisée du stock
            if not reward.stock or reward.stock < 1:
                order.statut = 'cancelled'
                db.session.commit()
                # Création des notifications
                notification_user = MyWittiNotification(
                    user_id=order.client_id,
                    message=f"Votre commande {order.id} a été annulée car l'article {reward.libelle} n'est pas disponible en stock."
                )
                notification_admin = MyWittiNotification(
                    user_id=admin.id,
                    message=f"La commande {order.id} a été annulée car l'article {reward.libelle} n'est pas disponible en stock."
                )
                db.session.add_all([notification_user, notification_admin])
                db.session.commit()
                return {"msg": f"Commande {order_id} annulée car stock insuffisant", "status": order.statut}, 200

            # Récupération sécurisée du client
            customer = MyWittiClient.query.filter_by(id=order.client_id).first()
            if not customer:
                return {"msg": "Client non trouvé"}, 404

            # Vérification sécurisée du solde client
            if customer.jetons < (reward.jetons or 0):
                return {"msg": "Jetons insuffisants pour le client"}, 400

            # Récupération de l'agence du client
            compte = MyWittiCompte.query.filter_by(customer_code=customer.customer_code).first()
            agence_name = compte.agence if compte and compte.agence else "votre agence"

            # Validation sécurisée de la commande
            order.statut = 'validated'
            customer.jetons -= (reward.jetons or 0)  # Débit des jetons lors de la validation
            # Mise à jour sécurisée du stock
            reward.stock -= 1
            # Création sécurisée des notifications
            customer_name = f"{customer.first_name} {customer.short_name}" if customer.first_name and customer.short_name else "Client"
            notification_user = MyWittiNotification(
                user_id=customer.user_id,
                message=f"Votre commande {order.id} de {reward.libelle} a été validée. Passez à l'agence {agence_name} pour la récupérer."
            )
            notification_admin = MyWittiNotification(
                user_id=admin.id,
                message=f"La commande {order.id} de {customer_name} pour {reward.libelle} a été validée."
            )
            db.session.add_all([notification_user, notification_admin])
            db.session.commit()
            return {"msg": f"Commande {order_id} validée avec succès", "status": order.statut}
        except Exception as e:
            db.session.rollback()
            return {"msg": f"Erreur lors de la validation: {str(e)}"}, 500

class CancelOrder(Resource):
    @jwt_required()
    @api.marshal_with(order_update_response_model)
    def put(self, order_id):
        try:
            # Vérification sécurisée des autorisations super admin
            admin_identifiant = get_jwt_identity()
            admin = MyWittiUser.query.filter_by(user_id=admin_identifiant).first()
            if not admin or not admin.is_superuser:
                return {"msg": "Seuls les super admins peuvent annuler les commandes"}, 403

            # Récupération sécurisée de la commande
            order = MyWittiLotsClaims.query.get(order_id)
            if not order:
                return {"msg": "Commande non trouvée"}, 404
            if order.statut == 'validated':
                return {"msg": "Une commande validée ne peut pas être annulée"}, 400
            if order.statut == 'cancelled':
                return {"msg": "La commande est déjà annulée"}, 400

            # Récupération de la récompense pour le message
            reward = MyWittiLot.query.get(order.lot_id)
            reward_name = reward.libelle if reward else "Article"

            # Annulation sécurisée de la commande (pas de débit de jetons)
            order.statut = 'cancelled'
            # Création sécurisée des notifications
            notification_user = MyWittiNotification(
                user_id=order.client_id,
                message=f"Votre commande {order.id} de {reward_name} a été annulée. Vos jetons n'ont pas été débités."
            )
            notification_admin = MyWittiNotification(
                user_id=admin.id,
                message=f"La commande {order.id} a été annulée."
            )
            db.session.add_all([notification_user, notification_admin])
            db.session.commit()
            return {"msg": f"Commande {order_id} annulée avec succès", "status": order.statut}
        except Exception as e:
            db.session.rollback()
            return {"msg": f"Erreur lors de l'annulation: {str(e)}"}, 500

# Enregistrement des ressources
api.add_resource(AdminOrders, '/orders')
api.add_resource(AdminOrderDetail, '/orders/<int:order_id>')
api.add_resource(ValidateOrder, '/orders/<int:order_id>/validate')
api.add_resource(CancelOrder, '/orders/<int:order_id>/cancel')
