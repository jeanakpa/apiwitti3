from flask import request
from flask_restx import Resource, fields
from flask_jwt_extended import jwt_required, get_jwt_identity
from Models.mywitti_users import MyWittiUser
from Models.mywitti_support_request import MyWittiSupportRequest
from Admin.views import api
from extensions import db

support_update_model = api.model('SupportUpdate', {
    'status': fields.String(required=False, description='Nouveau statut (Pending, In Progress, Resolved, Closed)'),
    'response': fields.String(required=False, description='Réponse de l’admin')
})

@api.route('/support/requests')
class AdminSupportRequests(Resource):
    @jwt_required()
    def get(self):
        admin_id = get_jwt_identity()
        admin = MyWittiUser.query.filter_by(user_id=admin_id).first()
        if not admin or not (admin.is_admin or admin.is_superuser):
            api.abort(403, "Accès interdit")

        requests = MyWittiSupportRequest.query.order_by(MyWittiSupportRequest.created_at.desc()).all()
        return [r.to_dict() for r in requests], 200

class SupportRequestList(Resource):
    @jwt_required()
    def get(self):
        admin_id = get_jwt_identity()
        admin = MyWittiUser.query.filter_by(user_id=admin_id).first()
        if not admin or not (admin.is_admin or admin.is_superuser):
            api.abort(403, "Accès interdit")

        requests = MyWittiSupportRequest.query.all()
        return [r.to_dict() for r in requests], 200


@api.route('/support/requests/<int:request_id>')
class AdminSupportRequestDetail(Resource):
    @jwt_required()
    @api.expect(support_update_model)
    def put(self, request_id):
        admin_id = get_jwt_identity()
        admin = MyWittiUser.query.filter_by(user_id=admin_id).first()
        if not admin or not (admin.is_admin or admin.is_superuser):
            api.abort(403, "Accès interdit")

        data = request.get_json()
        support_request = MyWittiSupportRequest.query.get(request_id)

        if not support_request:
            return {"message": "Demande introuvable"}, 404

        if "status" in data:
            support_request.status = data["status"]
        if "response" in data:
            support_request.response = data["response"]

        db.session.commit()
        return {"message": "Demande mise à jour avec succès", "request": support_request.to_dict()}, 200
