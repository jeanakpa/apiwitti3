from flask_restx import Resource, fields, Namespace
from flask_jwt_extended import jwt_required, get_jwt_identity
from Models.mywitti_users import MyWittiUser
from Models.mywitti_client import MyWittiClient
from Models.mywitti_lots import MyWittiLot
from Models.mywitti_lots_claims import MyWittiLotsClaims
from Models.mywitti_jetons_transactions import MyWittiJetonsTransactions
from extensions import db
from sqlalchemy.sql import desc, func
from cachetools import TTLCache
from datetime import datetime, date, timedelta


# Namespace
stats_ns = Namespace('stats', description='Statistics operations')

# Modèle pour le graphe évolutif
daily_purchases_model = stats_ns.model('DailyPurchasesChart', {
    'labels': fields.List(fields.String, description='Dates du mois'),
    'data': fields.List(fields.Integer, description='Nombre d’achats validés par jour')
})
# Modèle Stats général
stats_model = stats_ns.model('Stats', {
    'total_customers': fields.Integer(description='Total Customers'),
    'top_customer_tokens': fields.String(description='Customer with Most Tokens'),
    'pending_orders': fields.Integer(description='Pending Orders'),
    'cancelled_orders': fields.Integer(description='Cancelled Orders'),
    'validated_orders': fields.Integer(description='Validated Orders'),
    'most_purchased_reward': fields.String(description='Most Purchased Reward')
})

# Cache TTL 5 min
stats_cache = TTLCache(maxsize=100, ttl=300)

# Helpers
def get_top_customer():
    top_customer = MyWittiClient.query.order_by(MyWittiClient.jetons.desc()).first()
    if top_customer and top_customer.first_name and top_customer.short_name:
        return f"{top_customer.first_name} {top_customer.short_name} ({top_customer.jetons} jetons)"
    return "N/A"

def get_most_purchased_reward():
    if 'most_purchased_reward' in stats_cache:
        return stats_cache['most_purchased_reward']

    query = db.session.query(
        MyWittiLot.libelle,
        func.count(MyWittiLotsClaims.lot_id).label('purchase_count')
    ).join(
        MyWittiLotsClaims,
        MyWittiLot.id == MyWittiLotsClaims.lot_id
    ).filter(
        MyWittiLotsClaims.statut == 'validated'
    ).group_by(
        MyWittiLot.id, MyWittiLot.libelle
    ).order_by(desc('purchase_count')).limit(1).first()

    if query:
        libelle, count = query
        result = f"{libelle} ({count} achat{'s' if count > 1 else ''})"
    else:
        result = "N/A"

    stats_cache['most_purchased_reward'] = result
    return result

# Resource Stats général
class Stats(Resource):
    @jwt_required()
    @stats_ns.marshal_with(stats_model)
    def get(self):
        try:
            user_id = get_jwt_identity()
            user = MyWittiUser.query.filter_by(user_id=user_id).first()
            if not user or not (user.is_admin or user.is_superuser):
                stats_ns.abort(403, "Accès interdit - Droits administrateur requis")

            total_customers = MyWittiClient.query.count()
            top_customer_tokens = get_top_customer()
            pending_orders = MyWittiLotsClaims.query.filter_by(statut='pending').count()
            cancelled_orders = MyWittiLotsClaims.query.filter_by(statut='cancelled').count()
            validated_orders = MyWittiLotsClaims.query.filter_by(statut='validated').count()
            most_purchased_reward = get_most_purchased_reward()

            return {
                'total_customers': total_customers,
                'top_customer_tokens': top_customer_tokens,
                'pending_orders': pending_orders,
                'cancelled_orders': cancelled_orders,
                'validated_orders': validated_orders,
                'most_purchased_reward': most_purchased_reward
            }
        except Exception as e:
            stats_ns.abort(500, f"Erreur lors du calcul des statistiques: {str(e)}")

# Resource achats journaliers
class DailyPurchasesChart(Resource):
    @jwt_required()
    def get(self):
        try:
            user_id = get_jwt_identity()
            user = MyWittiUser.query.filter_by(user_id=user_id).first()
            if not user or not (user.is_admin or user.is_superuser):
                stats_ns.abort(403, "Accès interdit - Droits administrateur requis")

            today = datetime.utcnow().date()
            start_date = today - timedelta(days=29)

            results = (
                db.session.query(
                    func.date(MyWittiLotsClaims.date_reclamation).label('day'),
                    func.count(MyWittiLotsClaims.id).label('count')
                )
                .filter(
                    MyWittiLotsClaims.statut == 'validated',
                    MyWittiLotsClaims.date_reclamation >= start_date
                )
                .group_by('day')
                .order_by('day')
                .all()
            )

            day_counts = {r.day.strftime('%d-%m-%Y'): r.count for r in results}
            labels = [(start_date + timedelta(days=i)).strftime('%d-%m-%Y') for i in range(30)]
            data = [day_counts.get(day, 0) for day in labels]

            return {'labels': labels, 'data': data}

        except Exception as e:
            stats_ns.abort(500, f"Erreur lors de la récupération des achats journaliers: {str(e)}")

#
class DailyOrdersChart(Resource):
    @jwt_required()
    def get(self):
        try:
            # Vérification droits admin
            user_id = get_jwt_identity()
            user = MyWittiUser.query.filter_by(user_id=user_id).first()
            if not user or not (user.is_admin or user.is_superuser):
                return {"message": "Accès interdit"}, 403

            today = date.today()
            first_day = today.replace(day=1)
            last_day = (first_day.replace(month=first_day.month % 12 + 1, day=1) - timedelta(days=1))

            # Récupération des commandes par jour (toutes statuts)
            daily_counts = db.session.query(
                func.date(MyWittiLotsClaims.date_reclamation).label('day'),
                func.count(MyWittiLotsClaims.id)
            ).filter(
                MyWittiLotsClaims.date_reclamation >= first_day,
                MyWittiLotsClaims.date_reclamation <= last_day
            ).group_by('day').all()

            # Construire le tableau complet du mois
            day_labels = [(first_day + timedelta(days=i)) for i in range((last_day - first_day).days + 1)]
            data_dict = {d: 0 for d in day_labels}
            for day, count in daily_counts:
                data_dict[day] = count

            labels = [d.strftime("%Y-%m-%d") for d in day_labels]
            data = [data_dict[d] for d in day_labels]

            return {"labels": labels, "data": data}

        except Exception as e:
            return {"message": f"Erreur lors de la récupération des commandes journalières: {str(e)}"}, 500

# Export
__all__ = ['Stats', 'DailyPurchasesChart', 'stats_ns', 'stats_model']
