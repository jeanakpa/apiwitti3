# admin/resources/notifications.py
from flask import request
from flask_restx import Resource, fields
from flask_jwt_extended import jwt_required, get_jwt_identity
from Models.mywitti_users import MyWittiUser
from Models.mywitti_notification import MyWittiNotification
from Admin.views import api
from extensions import db

notification_model = api.model('Notification', {
    'id': fields.Integer(description='Notification ID'),
    'message': fields.String(description='Notification message'),
    'created_at': fields.String(description='Creation date'),
    'is_read': fields.Boolean(description='Whether the notification is read')
})

notifications_response_model = api.model('NotificationsResponse', {
    'msg': fields.String(description='Success message'),
    'notifications': fields.List(fields.Nested(notification_model), description='List of notifications')
})

notification_update_model = api.model('NotificationUpdate', {
    'is_read': fields.Boolean(description='Mark as read')
})

class AdminNotifications(Resource):
    @jwt_required()
    @api.marshal_with(notifications_response_model)
    def get(self):
        try:
            # Vérification sécurisée des autorisations admin
            admin_identifiant = get_jwt_identity()
            admin = MyWittiUser.query.filter_by(user_id=admin_identifiant).first()
            if not admin or not (admin.is_admin or admin.is_superuser):
                return {"msg": "Utilisateur non autorisé - Droits administrateur requis"}, 403
            
            # Récupération sécurisée des notifications de l'admin
            notifications = MyWittiNotification.query.filter_by(
                user_id=admin.id
            ).order_by(MyWittiNotification.created_at.desc()).all()
            
            notifications_data = [{
                'id': notification.id,
                'message': notification.message or "Message vide",
                'created_at': notification.created_at.strftime('%Y-%m-%d %H:%M:%S') if notification.created_at else "Unknown",
                'is_read': notification.is_read or False
            } for notification in notifications]
            
            return {
                'msg': 'Notifications récupérées avec succès', 
                'notifications': notifications_data
            }
        except Exception as e:
            return {"msg": f"Erreur lors de la récupération des notifications: {str(e)}"}, 500

class AdminNotificationDetail(Resource):
    @jwt_required()
    def delete(self, notification_id):
        try:
            # Vérification sécurisée des autorisations admin
            admin_identifiant = get_jwt_identity()
            admin = MyWittiUser.query.filter_by(user_id=admin_identifiant).first()
            if not admin or not (admin.is_admin or admin.is_superuser):
                return {"msg": "Utilisateur non autorisé - Droits administrateur requis"}, 403

            # Validation de l'ID de notification
            try:
                notification_id = int(notification_id)
            except (ValueError, TypeError):
                return {"msg": "ID de notification invalide"}, 400

            # Récupération sécurisée de la notification
            notification = MyWittiNotification.query.filter_by(
                id=notification_id, 
                user_id=admin.id
            ).first()
            
            if not notification:
                return {"msg": "Notification non trouvée ou non autorisée"}, 404

            # Suppression sécurisée de la notification
            db.session.delete(notification)
            db.session.commit()
            
            return {"msg": "Notification supprimée avec succès"}, 200

        except Exception as e:
            db.session.rollback()
            return {"msg": f"Erreur lors de la suppression: {str(e)}"}, 500

    @jwt_required()
    @api.expect(notification_update_model)
    def patch(self, notification_id):
        try:
            # Vérification sécurisée des autorisations admin
            admin_identifiant = get_jwt_identity()
            admin = MyWittiUser.query.filter_by(user_id=admin_identifiant).first()
            if not admin or not (admin.is_admin or admin.is_superuser):
                return {"msg": "Utilisateur non autorisé - Droits administrateur requis"}, 403

            # Validation de l'ID de notification
            try:
                notification_id = int(notification_id)
            except (ValueError, TypeError):
                return {"msg": "ID de notification invalide"}, 400

            # Récupération sécurisée de la notification
            notification = MyWittiNotification.query.filter_by(
                id=notification_id, 
                user_id=admin.id
            ).first()
            
            if not notification:
                return {"msg": "Notification non trouvée ou non autorisée"}, 404

            # Récupération des données de mise à jour (optionnel)
            data = request.get_json() if request.is_json else {}
            
            # Mise à jour sécurisée du statut de lecture
            # Si pas de données JSON, on marque automatiquement comme lu
            if not data or 'is_read' not in data:
                notification.is_read = True
            else:
                notification.is_read = bool(data['is_read'])

            db.session.commit()
            
            return {
                'msg': 'Notification mise à jour avec succès', 
                'notification': {
                    'id': notification.id,
                    'message': notification.message or "Message vide",
                    'created_at': notification.created_at.strftime('%Y-%m-%d %H:%M:%S') if notification.created_at else "Unknown",
                    'is_read': notification.is_read or False
                }
            }, 200

        except Exception as e:
            db.session.rollback()
            return {"msg": f"Erreur lors de la mise à jour: {str(e)}"}, 500