# Account/views.py
from datetime import datetime
from flask import Blueprint, request, current_app
from flask_restx import Api, Resource, fields
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required
from werkzeug.security import check_password_hash
from extensions import db
from Models.mywitti_users import MyWittiUser
from Models.mywitti_client import MyWittiClient
import bcrypt

# =====================================================
# Blueprint & API
# =====================================================
accounts_bp = Blueprint('accounts', __name__)
api = Api(
    accounts_bp,
    doc='/doc/',
    version='1.0',
    title='Accounts API',
    description='API for account operations'
)

# =====================================================
# Models for Swagger
# =====================================================
login_model = api.model('Login', {
    'identifiant': fields.String(required=True, description='User identifier'),
    'password': fields.String(required=True, description='User password')
})

admin_login_model = api.model('AdminLogin', {
    'email': fields.String(required=True, description='Admin email'),
    'password': fields.String(required=True, description='Admin password')
})

signup_model = api.model('Signup', {
    'first_name': fields.String(required=True),
    'last_name': fields.String(required=True),
    'username': fields.String(required=True),
    'email': fields.String(required=True),
    'identifiant': fields.String(required=True),
    'password': fields.String(required=True)
})

login_response_model = api.model('LoginResponse', {
    'access_token': fields.String(description='JWT access token')
})

admin_login_response_model = api.model('AdminLoginResponse', {
    'access_token': fields.String(description='JWT access token'),
    'role': fields.String(description='Admin role'),
    'name': fields.String(description='Admin name'),
    'email': fields.String(description='Admin email')
})

# =====================================================
# User Login Route
# =====================================================
@api.route('/login')
class Login(Resource):
    @api.expect(login_model)
    def post(self):
        data = api.payload
        identifiant = data.get('identifiant')
        password = data.get('password')

        try:
            user = db.session.query(MyWittiUser).filter_by(user_id=identifiant).first()
            if not user:
                current_app.logger.warning(f"Login failed: User with identifiant {identifiant} not found")
                return {"message": "Invalid identifiant or password"}, 401

            # Vérification du mot de passe (werkzeug ou bcrypt)
            password_valid = False
            try:
                password_valid = check_password_hash(user.password, password)
            except Exception:
                try:
                    password_valid = bcrypt.checkpw(password.encode('utf-8'), user.password.encode('utf-8'))
                except Exception as e:
                    current_app.logger.error(f"Password check error: {str(e)}")
                    password_valid = False

            if not password_valid:
                current_app.logger.warning(f"Login failed: Incorrect password for identifiant {identifiant}")
                return {"message": "Invalid identifiant or password"}, 401

            access_token = create_access_token(identity=identifiant)
            current_app.logger.info(f"User {identifiant} logged in successfully")
            return {"access_token": access_token}, 200

        except Exception as e:
            current_app.logger.error(f"Error during login: {str(e)}")
            import traceback
            current_app.logger.error(traceback.format_exc())
            return {"error": "Une erreur s'est produite lors de la connexion", "details": str(e)}, 500

# =====================================================
# Admin / SuperAdmin Login Route
# =====================================================
@api.route('/admin/login')
class AdminLogin(Resource):
    @api.expect(admin_login_model)
    @api.marshal_with(admin_login_response_model)
    def post(self):
        data = api.payload
        email = data.get('email')
        password = data.get('password')

        try:
            admin = db.session.query(MyWittiUser).filter_by(email=email).first()
            if not admin:
                current_app.logger.warning(f"Admin login failed: User with email {email} not found")
                return {"message": "Invalid email or password"}, 401

            # Vérification universelle du mot de passe
            password_valid = False
            try:
                password_valid = check_password_hash(admin.password, password)
            except Exception:
                try:
                    password_valid = bcrypt.checkpw(password.encode('utf-8'), admin.password.encode('utf-8'))
                except Exception as e:
                    current_app.logger.error(f"Password check error: {str(e)}")
                    password_valid = False

            if not password_valid:
                current_app.logger.warning(f"Admin login failed: Incorrect password for email {email}")
                return {"message": "Invalid email or password"}, 401

            # Vérifier rôle admin/superadmin
            if not (admin.is_admin or admin.is_superuser):
                current_app.logger.warning(f"Admin login failed: User {email} is not an admin")
                return {"message": "User is not an admin"}, 403

            access_token = create_access_token(identity=admin.user_id)
            current_app.logger.info(f"Admin {email} logged in successfully")

            return {
                "access_token": access_token,
                "role": "super_admin" if admin.is_superuser else "admin",
                "name": f"{admin.first_name} {admin.last_name}",
                "email": admin.email
            }, 200

        except Exception as e:
            current_app.logger.error(f"Error during admin login: {str(e)}")
            import traceback
            current_app.logger.error(traceback.format_exc())
            return {"error": str(e)}, 500
