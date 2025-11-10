from flask import Blueprint, current_app, request
from flask_restx import Api, Resource, fields
import uuid
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from Models.mywitti_client import MyWittiClient
from Models.mywitti_category import MyWittiCategory
from Models.mywitti_mouvement import MyWittiMouvement
from Models.mywitti_users import MyWittiUser
from Models.token_blacklist import TokenBlacklist
from extensions import db
from datetime import datetime, timedelta
from Models.mywitti_referral import MyWittiReferral
from Models.mywitti_notification import MyWittiNotification
from Models.mywitti_comptes import MyWittiCompte

customer_bp = Blueprint('customer', __name__)
reward_bp = Blueprint('reward', __name__)
api = Api(customer_bp, version='1.0', title='Customer API', description='API for customer operations')

# Define category ranges
CATEGORIES = [
    {"name": "Eco Premium", "code": "A", "min": 0, "max": 100},
    {"name": "Executive", "code": "B", "min": 100, "max": 1000},
    {"name": "Executive +", "code": "C", "min": 1000, "max": 3000},
    {"name": "First Class", "code": "D", "min": 3000, "max": float('inf')}
]

# Define response models for dashboard
dashboard_model = api.model('Dashboard', {
    'category': fields.String(description='Customer category'),
    'jetons': fields.Integer(description='Total jetons'),
    'percentage': fields.Float(description='Percentage within category range'),
    'short_name': fields.String(description='Short name'),
    'short_name_with_title': fields.String(description='Short name with title (M. or Mme.)'),
    'full_name_with_title': fields.String(description='Full name with title (M. or Mme.)'),
    'tokens_to_next_tier': fields.Integer(description='Jetons needed to reach next tier'),
    'last_transactions': fields.List(fields.Raw, description='Last 5 transactions')
})
# Define response models for transactions
transaction_model = api.model('Transaction', {
    'libelle' : fields.String(description='Transaction label'),
    'date': fields.String(description='Transaction date'),
    'amount': fields.String(description='Amount'),
    'type': fields.String(description='Transaction type (DEPOSIT/WITHDRAWAL)')
})

trends_model = api.model('Trends', {
    'deposit_percentage': fields.Float(description='Percentage of deposit transactions'),
    'withdrawal_percentage': fields.Float(description='Percentage of withdrawal transactions')
})

transactions_response_model = api.model('TransactionsResponse', {
    'transactions': fields.List(fields.Nested(transaction_model), description='List of transactions'),
    'total_transactions': fields.Integer(description='Total number of transactions'),
    'period_start': fields.String(description='Start of the period'),
    'period_end': fields.String(description='End of the period'),
    'trends': fields.Nested(trends_model, description='Transaction trends (deposit and withdrawal percentages)')
})

# Define response model for notifications
notification_model = api.model('Notification', {
    'id': fields.Integer(description='Notification ID'),
    'message': fields.String(description='Notification message'),
    'created_at': fields.String(description='Creation date'),
    'is_read': fields.Boolean(description='Whether the notification has been read')
})

notifications_response_model = api.model('NotificationsResponse', {
    'msg': fields.String(description='Success message'),
    'notifications': fields.List(fields.Nested(notification_model), description='List of notifications')
})

notification_update_model = api.model('NotificationUpdate', {
    'id': fields.Integer(required=True, description='ID de la notification'),
    'is_read': fields.Boolean(required=True, description='Mark notification as read/unread')
})
# Define response model for profile
profile_model = api.model('Profile', {
    'first_name': fields.String(description='Customer first name'),
    'short_name': fields.String(description='Customer short name'),
    'agency': fields.String(description='Customer agency'),
    'jetons': fields.Integer(description='Total jetons'),
    'category': fields.String(description='Customer category'),
    'percentage': fields.Float(description='Percentage within category range'),
    'tokens_to_next_tier': fields.Integer(description='Jetons needed to reach next tier')
})

#Invitation de parrainage
referral_model = api.model('Referral', {
    'referral_link': fields.String(description='Lien de parrainage'),
    'referred_email': fields.String(description='Email de l\'ami invité'),
    'status': fields.String(description='Statut du parrainage'),
    'created_at': fields.DateTime(description='Date de création')
})

# Define response model for logout
logout_response_model = api.model('LogoutResponse', {
    'msg': fields.String(description='Logout message')
})


def format_name_with_title(first_name, gender):
    """
    Formate le nom avec le titre approprié selon le genre
    Args:
        first_name (str): Prénom du client
        gender (str): Genre du client ('MALE', 'M', 'FEMALE', ou 'F')
    Returns:
        str: Nom formaté avec titre (ex: 'M. Koffi' ou 'Mme. Koffi')
    """
    if not first_name:
        return ""

    # Nettoyer le prénom (enlever les espaces en début/fin)
    first_name = first_name.strip()

    if gender == 'MALE' or gender == 'M':
        return f"M. {first_name}"
    elif gender == 'FEMALE' or gender == 'F':
        return f"Mme. {first_name}"
    else:
        # Si le genre n'est pas spécifié, retourner juste le prénom
        return first_name


def format_short_name_with_title(short_name, gender):
    """
    Formate le short_name avec le titre approprié selon le genre
    Args:
        short_name (str): Short name du client
        gender (str): Genre du client ('MALE', 'M', 'FEMALE', ou 'F')
    Returns:
        str: Short name formaté avec titre (ex: 'M. EBA' ou 'Mme. EBA')
    """
    if not short_name:
        return ""

    # Nettoyer le short_name (enlever les espaces en début/fin)
    short_name = short_name.strip()

    if gender == 'MALE' or gender == 'M':
        return f"M. {short_name}"
    elif gender == 'FEMALE' or gender == 'F':
        return f"Mme. {short_name}"
    else:
        # Si le genre n'est pas spécifié, retourner juste le short_name
        return short_name


@api.route('/dashboard')
class CustomerDashboard(Resource):
    @jwt_required()
    @api.marshal_with(dashboard_model)
    def get(self):
        try:
            identifiant = get_jwt_identity()
            current_app.logger.info(f"[Dashboard] JWT Identity reçu: {identifiant}")

            if not identifiant:
                current_app.logger.error("[Dashboard] JWT identity manquant")
                return {"error": "JWT identity missing"}, 400

            # Récupération du client
            customer = db.session.query(MyWittiClient).filter_by(customer_code=identifiant).first()
            if not customer:
                current_app.logger.warning(f"[Dashboard] Aucun client trouvé pour: {identifiant}")
                return {"message": "Customer not found"}, 404

            current_app.logger.info(f"[Dashboard] Client trouvé: {customer.customer_code}, jetons: {customer.jetons}, gender: {customer.gender}")

            customer_code = customer.customer_code
            jetons = customer.jetons or 0

            # Calcul de la catégorie et du pourcentage
            try:
                category_name = customer.category.category_name if customer.category else "Inconnue"
            except AttributeError as e:
                current_app.logger.error(f"[Dashboard] Erreur accès category: {str(e)}")
                category_name = "Inconnue"

            current_app.logger.info(f"[Dashboard] Category: {category_name}")

            percentage = 0
            tokens_to_next_tier = 0
            for i, cat in enumerate(CATEGORIES):
                if cat['min'] <= jetons < cat['max']:
                    range_width = cat['max'] - cat['min']
                    position_in_range = jetons - cat['min']
                    percentage = (position_in_range / range_width) * 100 if range_width > 0 else 0
                    if i + 1 < len(CATEGORIES):
                        tokens_to_next_tier = CATEGORIES[i + 1]['min'] - jetons
                    break

            # Récupération des dernières transactions (5)
            latest_transactions = []
            try:
                derniers_mouvements = db.session.query(MyWittiMouvement).filter(
                    MyWittiMouvement.customer_code == customer_code
                ).order_by(
                    MyWittiMouvement.booking_date.desc()
                ).limit(5).all()

                for mv in derniers_mouvements:
                    if mv.credit and mv.credit > 0:
                        tx_type = "Dépôt"
                        amount = mv.credit
                    elif mv.debit and mv.debit > 0:
                        tx_type = "Retrait"
                        amount = mv.debit
                    else:
                        continue

                    latest_transactions.append({
                        'date': mv.booking_date.strftime('%d-%m-%Y') if mv.booking_date else None,
                        'amount': str(amount),
                        'type': tx_type,
                        'libelle': mv.libelle or ""
                    })
            except Exception as e:
                current_app.logger.warning(f"[Dashboard] Impossible de récupérer les transactions: {str(e)}")
                latest_transactions = []

            # Formatage des noms
            try:
                short_name = format_short_name_with_title(customer.short_name, customer.gender)
                short_name_with_title = format_short_name_with_title(customer.short_name, customer.gender)
                full_name_with_title = format_name_with_title(customer.first_name, customer.gender)
            except Exception as e:
                current_app.logger.error(f"[Dashboard] Erreur formatage noms: {str(e)}")
                short_name = customer.short_name or ""
                short_name_with_title = customer.short_name or ""
                full_name_with_title = customer.first_name or ""

            # Réponse conforme au modèle dashboard_model
            response = {
                "category": category_name,
                "jetons": jetons,
                "percentage": round(percentage, 2),
                "short_name": short_name,
                "short_name_with_title": short_name_with_title,
                "full_name_with_title": full_name_with_title,
                "tokens_to_next_tier": tokens_to_next_tier,
                "last_transactions": latest_transactions or []
            }

            current_app.logger.info(f"[Dashboard] Réponse générée pour {customer_code}: {response}")
            return response, 200

        except Exception as e:
            current_app.logger.error(f"[Dashboard] Erreur serveur: {str(e)}", exc_info=True)
            import traceback
            current_app.logger.error(f"[Dashboard] Traceback: {traceback.format_exc()}")
            return {"error": "Internal server error"}, 500


@api.route('/transactions')
class CustomerTransactions(Resource):
    @jwt_required()
    def get(self):
        try:
            # Récupération sécurisée de l'identité du JWT
            user_identity = get_jwt_identity()
            customer_code = user_identity.get('customer_code') if isinstance(user_identity, dict) else user_identity

            if not customer_code:
                current_app.logger.warning("[Transactions] Customer code manquant dans le JWT")
                return {"error": "Customer code missing in JWT"}, 400

            # Paramètres de date
            start_date_str = request.args.get('start_date')
            end_date_str = request.args.get('end_date')

            try:
                period_start = datetime.strptime(start_date_str, '%Y-%m-%d') if start_date_str else None
                period_end = datetime.strptime(end_date_str, '%Y-%m-%d') if end_date_str else None
            except ValueError:
                return jsonify({"error": "Format de date invalide. Utilisez le format YYYY-MM-DD."}), 400

            # Filtrage des transactions
            query = MyWittiMouvement.query.filter_by(customer_code=customer_code)

            if period_start:
                query = query.filter(MyWittiMouvement.booking_date >= period_start)
            if period_end:
                query = query.filter(MyWittiMouvement.booking_date <= period_end)

            transactions = query.order_by(MyWittiMouvement.booking_date.desc()).all()

            # Préparation de la liste pour le frontend
            transactions_list = []
            for t in transactions:
                if t.credit and t.credit > 0:
                    tx_type = "Dépôt"
                    amount = t.credit
                elif t.debit and t.debit > 0:
                    tx_type = "Retrait"
                    amount = t.debit
                else:
                    continue

                transactions_list.append({
                    "id": t.id,
                    "libelle": t.libelle or "",
                    "type": tx_type,
                    "amount": str(amount),
                    "solde": getattr(t, 'solde', None),  # si tu n'as pas de solde, tu peux l'ignorer
                    "date_operation": t.booking_date.strftime('%d-%m-%Y') if t.booking_date else None
                })

            response = {
                "customer_code": customer_code,
                "total_transactions": len(transactions_list),
                "transactions": transactions_list,
                "period_start": start_date_str,
                "period_end": end_date_str
            }

            return response, 200

        except Exception as e:
            current_app.logger.error(f"[Transactions] Erreur serveur: {str(e)}", exc_info=True)
            return {"error": "Internal server error"}, 500

@api.route('/notifications')
class CustomerNotifications(Resource):
    @jwt_required()
    @api.marshal_with(notifications_response_model)
    def get(self):
        try:
            identifiant = get_jwt_identity()
            current_app.logger.info(f"JWT Identity: {identifiant}")

            customer = db.session.query(MyWittiClient).filter_by(customer_code=identifiant).first()
            if not customer:
                current_app.logger.warning(f"No customer found for identifiant: {identifiant}")
                return {"message": "Customer not found"}, 404

            notifications = MyWittiNotification.query.filter_by(
                user_id=customer.user_id
            ).order_by(MyWittiNotification.created_at.desc()).all()

            notifications_data = [{
                'id': notification.id,
                'message': notification.message,
                'created_at': notification.created_at.strftime('%d-%m-%Y %H:%M:%S') if notification.created_at else "Inconnue",
                'is_read': notification.is_read if hasattr(notification, 'is_read') else False
            } for notification in notifications]

            return {
                'msg': 'Notifications récupérées avec succès',
                'notifications': notifications_data
            }, 200
        except Exception as e:
            current_app.logger.error(f"Error fetching notifications: {str(e)}")
            return {"error": "Internal server error"}, 500

    @jwt_required()
    @api.expect(notification_update_model, validate=True)
    def patch(self):
        """
        Marquer une notification comme lue / non lue
        """
        try:
            identifiant = get_jwt_identity()
            customer = db.session.query(MyWittiClient).filter_by(customer_code=identifiant).first()
            if not customer:
                return {"message": "Customer not found"}, 404

            data = request.json
            notification_id = data.get("id")
            is_read = data.get("is_read")

            notification = MyWittiNotification.query.filter_by(
                id=notification_id,
                user_id=customer.user_id
            ).first()

            if not notification:
                return {"message": "Notification not found"}, 404

            notification.is_read = is_read
            db.session.commit()

            return {
                "msg": f"Notification {notification_id} updated successfully",
                "notification": {
                    "id": notification.id,
                    "message": notification.message,
                    "created_at": notification.created_at.strftime('%d-%m-%Y %H:%M:%S') if notification.created_at else "Inconnue",
                    "is_read": notification.is_read
                }
            }, 200

        except Exception as e:
            current_app.logger.error(f"Error updating notification: {str(e)}", exc_info=True)
            return {"error": "Internal server error"}, 500


@api.route('/profile')
class CustomerProfile(Resource):
    @jwt_required()
    @api.marshal_with(profile_model)
    def get(self):
        try:
            identifiant = get_jwt_identity()
            current_app.logger.info(f"JWT Identity: {identifiant}")

            # Extraction sécurisée du code client
            customer_code = identifiant.get('customer_code') if isinstance(identifiant, dict) else identifiant

            customer = db.session.query(MyWittiClient).filter_by(customer_code=customer_code).first()
            if not customer:
                current_app.logger.warning(f"No customer found for customer_code: {customer_code}")
                return {"message": "Customer not found"}, 404

            # Calcul de la catégorie et des pourcentages
            category = customer.category
            category_name = category.category_name if category else "Inconnue"

            jetons = customer.jetons or 0
            percentage = 0
            tokens_to_next_tier = 0
            for i, cat in enumerate(CATEGORIES):
                if cat['min'] <= jetons < cat['max']:
                    range_width = cat['max'] - cat['min']
                    position_in_range = jetons - cat['min']
                    percentage = (position_in_range / range_width) * 100 if range_width > 0 else 0
                    if i + 1 < len(CATEGORIES):
                        tokens_to_next_tier = CATEGORIES[i + 1]['min'] - jetons
                    break

            profile = {
                "first_name": customer.first_name or "N/A",
                "short_name": customer.short_name or "N/A",
                "agency": "RGK",
                "jetons": jetons,
                "category": category_name,
                "percentage": round(percentage, 2),
                "tokens_to_next_tier": tokens_to_next_tier
            }

            current_app.logger.info(f"Profile retrieved for customer_code: {customer_code}")
            return profile, 200

        except Exception as e:
            current_app.logger.error(f"Error fetching profile: {str(e)}")
            return {"error": "Internal server error"}, 500


@api.route('/logout')
class CustomerLogout(Resource):
    @jwt_required()
    @api.marshal_with(logout_response_model)
    def post(self):
        try:
            # Récupération sécurisée du JTI du token
            jti = get_jwt()['jti']
            # Ajout du token à la liste noire
            blacklisted_token = TokenBlacklist(jti=jti)
            db.session.add(blacklisted_token)
            db.session.commit()

            current_app.logger.info(f"Customer logged out successfully, token JTI {jti} blacklisted")
            return {"msg": "Déconnexion réussie"}, 200
        except Exception as e:
            current_app.logger.error(f"Error during customer logout: {str(e)}")
            return {"error": "Internal server error"}, 500


# Systeme de parrainage

invite_model = api.model('Invite', {
    'email': fields.String(required=True, description='Email de l\'ami à inviter')
})

# Modèle pour la liste des parrainages
referrals_list_model = api.model('ReferralsList', {
    'referrals': fields.List(fields.Nested(referral_model), description='Liste des parrainages'),
    'total_referrals': fields.Integer(description='Nombre total de parrainages'),
    'pending_count': fields.Integer(description='Nombre de parrainages en attente'),
    'accepted_count': fields.Integer(description='Nombre de parrainages acceptés'),
    'rewarded_count': fields.Integer(description='Nombre de parrainages récompensés')
})

class InviteResource(Resource):
    @jwt_required()
    @api.expect(invite_model)
    def post(self):
        try:
            # Récupération sécurisée de l'utilisateur connecté
            identifiant = get_jwt_identity()
            user = MyWittiUser.query.filter_by(user_id=identifiant).first()
            if not user:
                return {'message': 'Utilisateur non trouvé'}, 404

            # Récupération et validation de l'email de l'ami
            data = request.get_json()
            email = data.get('email')
            if not email:
                return {'message': 'Email requis'}, 400

            # Validation basique de l'email
            if '@' not in email or '.' not in email:
                return {'message': 'Format d\'email invalide'}, 400

            # Vérification si l'email existe déjà dans les parrainages
            existing_referral = MyWittiReferral.query.filter_by(referred_email=email).first()
            if existing_referral:
                return {'message': 'Cet email a déjà été invité'}, 400

            # Création sécurisée d'un nouveau parrainage
            referral_code = str(uuid.uuid4())
            referral = MyWittiReferral(
                referrer_id=user.id,
                referred_email=email,
                referral_code=referral_code,
                status='pending'
            )
            db.session.add(referral)
            db.session.commit()

            referral_link = f"http://127.0.0.1:5000/accounts/refer/{referral_code}"
            return {
                'message': 'Invitation envoyée',
                'referral_link': referral_link
            }, 201

        except Exception as e:
            current_app.logger.error(f"Error creating referral: {str(e)}")
            db.session.rollback()
            return {"error": "Internal server error"}, 500

class MyReferralsResource(Resource):
    @jwt_required()
    @api.marshal_with(referrals_list_model)
    def get(self):
        try:
            # Récupération sécurisée de l'utilisateur connecté
            identifiant = get_jwt_identity()
            user = MyWittiUser.query.filter_by(user_id=identifiant).first()
            if not user:
                return {'message': 'Utilisateur non trouvé'}, 404
            # Récupération sécurisée des parrainages de l'utilisateur
            referrals = MyWittiReferral.query.filter_by(referrer_id=user.id).order_by(MyWittiReferral.created_at.desc()).all()

            referrals_data = []
            pending_count = 0
            accepted_count = 0
            rewarded_count = 0

            for referral in referrals:
                # Compter les statuts
                if referral.status == 'pending':
                    pending_count += 1
                elif referral.status == 'accepted':
                    accepted_count += 1
                elif referral.status == 'rewarded':
                    rewarded_count += 1

                referral_data = {
                    'referral_link': f"http://127.0.0.1:5000/accounts/refer/{referral.referral_code}",
                    'referred_email': referral.referred_email,
                    'status': referral.status,
                    'created_at': referral.created_at.isoformat() if referral.created_at else None
                }
                referrals_data.append(referral_data)

            return {
                'referrals': referrals_data,
                'total_referrals': len(referrals_data),
                'pending_count': pending_count,
                'accepted_count': accepted_count,
                'rewarded_count': rewarded_count
            }, 200

        except Exception as e:
            current_app.logger.error(f"Error fetching referrals: {str(e)}")
            return {"error": "Internal server error"}, 500

api.add_resource(InviteResource, '/invite')
api.add_resource(MyReferralsResource, '/my-referrals')
accounts_list_model = api.model('AccountList', {
    'agency': fields.String(description='Nom de l\'agence'),
    'client_name': fields.String(description='Nom complet du client'),
    'account_number': fields.String(description='Numéro de compte'),
    'customer_code': fields.String(description='Code client'),
    'country': fields.String(description='Pays de l\'agence'),
    'primary': fields.Boolean(description='Compte principal')
})

@api.route('/comptes')
class CustomerAccounts(Resource):
    @jwt_required()
    @api.marshal_list_with(accounts_list_model)
    def get(self):
        try:
            identifiant = get_jwt_identity()
            current_app.logger.info(f"[Comptes] JWT Identity: {identifiant}")

            # Récupérer le client
            customer = db.session.query(MyWittiClient).filter_by(customer_code=identifiant).first()
            if not customer:
                current_app.logger.warning(f"[Comptes] Aucun client trouvé pour {identifiant}")
                return [], 404

            # Récupérer tous les comptes liés
            comptes = db.session.query(MyWittiCompte).filter_by(customer_code=customer.customer_code).all()
            if not comptes:
                return [], 404

            # Récupérer le pays sélectionné depuis la configuration partagée
            selected_country = None

            # Log pour débugger
            current_app.logger.info(f"[Comptes] Customer code: {customer.customer_code}")
            current_app.logger.info(f"[Comptes] Pays par défaut du client: {getattr(customer, 'country', 'Non défini')}")

            try:
                # Import de la configuration partagée
                from shared_config import get_customer_country
                selected_country = get_customer_country(customer.customer_code)
                if selected_country:
                    current_app.logger.info(f"[Comptes] Pays sélectionné récupéré: {selected_country}")
                else:
                    current_app.logger.info(f"[Comptes] Aucun pays sélectionné trouvé pour customer_code: {customer.customer_code}")
            except Exception as e:
                current_app.logger.warning(f"[Comptes] Impossible de récupérer le pays sélectionné: {str(e)}")

            accounts_data = []
            for i, compte in enumerate(comptes):
                # Concaténation de short_name et first_name si besoin
                client_name = f"{customer.short_name or ''} {customer.first_name or ''}".strip()

                # Utiliser le pays sélectionné s'il est disponible, sinon utiliser le pays par défaut
                country_to_display = selected_country if selected_country else getattr(customer, 'country', 'Inconnu')

                # Log pour débugger
                current_app.logger.info(f"[Comptes] Compte {i+1}: pays affiché = {country_to_display} (sélectionné: {selected_country}, défaut: {getattr(customer, 'country', 'Inconnu')})")
                accounts_data.append({
                    "agency": compte.agence or "N/A",
                    "client_name": client_name if client_name else "N/A",
                    "account_number": compte.numero_compte or "N/A",
                    "customer_code": customer.customer_code,
                    "country": country_to_display
                })

            current_app.logger.info(f"[Comptes] {len(accounts_data)} comptes trouvés pour {identifiant}, pays affiché: {selected_country or 'défaut'}")
            return accounts_data, 200
        except Exception as e:
            current_app.logger.error(f"[Comptes] Erreur serveur: {str(e)}", exc_info=True)
            return {"error": "Internal server error"}, 500
