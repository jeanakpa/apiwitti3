# Admin/resources/stock.py
import os
from flask import request
from flask_restx import Resource, fields
from flask_jwt_extended import jwt_required, get_jwt_identity
from Models.mywitti_users import MyWittiUser
from Models.mywitti_lots import MyWittiLot
from Models.mywitti_lots_claims import MyWittiLotsClaims
from extensions import db
from datetime import datetime
from Admin.views import api
from sqlalchemy.exc import IntegrityError
from werkzeug.utils import secure_filename

# Configuration sécurisée pour le dossier d'upload des images
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB max

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def allowed_file(filename):
    """Vérification sécurisée du type de fichier"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def validate_file_size(file):
    """Vérification sécurisée de la taille du fichier"""
    file.seek(0, 2)  # Aller à la fin du fichier
    size = file.tell()
    file.seek(0)  # Retourner au début
    return size <= MAX_FILE_SIZE

stock_model = api.model('Stock', {
    'id': fields.Integer(description='Stock ID'),
    'libelle': fields.String(description='Name of the item'),
    'jetons': fields.Integer(description='Price in Tokens'),
    'stock': fields.Integer(description='Quantity Available'),
    'recompense_image': fields.String(description='Image URL'),
    'category': fields.String(description='Category'),
    'created_at': fields.String(description='Creation date')
})

stock_input_model = api.model('StockInput', {
    'libelle': fields.String(required=True, description='Name of the item'),
    'jetons': fields.Integer(required=True, description='Price in Tokens'),
    'stock': fields.Integer(required=True, description='Quantity Available'),
    'category_id': fields.Integer(description='Category ID'),
    'recompense_image_url': fields.String(description='URL of the reward image (alternative to file upload)')
})

class StockList(Resource):
    @jwt_required()
    @api.marshal_with(stock_model, as_list=True)
    def get(self):
        try:
            # Vérification sécurisée des autorisations admin
            user_id = get_jwt_identity()
            user = MyWittiUser.query.filter_by(user_id=user_id).first()

            if not user or not (user.is_admin or user.is_superuser):
                api.abort(403, "Accès interdit - Droits administrateur requis")
            
            # Récupération sécurisée de tous les stocks
            stocks = MyWittiLot.query.all()
            return [{
                'id': stock.id,
                'libelle': stock.libelle or "Sans titre",
                'jetons': stock.jetons or 0,
                'stock': stock.stock or 0,
                'recompense_image': stock.recompense_image or "",
                'category': stock.category.category_name if stock.category else "Sans catégorie",
                'created_at': stock.created_at.strftime('%Y-%m-%d %H:%M:%S') if stock.created_at else "Date inconnue"
            } for stock in stocks]
        except Exception as e:
            api.abort(500, f"Erreur lors de la récupération des stocks: {str(e)}")

    @jwt_required()
    @api.expect(stock_input_model)
    @api.marshal_with(stock_model, code=201)
    def post(self):
        try:
            # Vérification sécurisée des autorisations super admin
            user_id = get_jwt_identity()
            user = MyWittiUser.query.filter_by(user_id=user_id).first()

            if not user or not user.is_superuser:
                api.abort(403, "Seuls les super admins peuvent ajouter du stock")

            # Récupération et validation des données
            data = request.get_json()
            if not data:
                api.abort(400, "Données JSON requises")

            # Validation des champs obligatoires
            required_fields = ['libelle', 'jetons', 'stock']
            for field in required_fields:
                if not data.get(field):
                    api.abort(400, f"Le champ {field} est requis")

            # Validation des valeurs numériques
            try:
                jetons = int(data['jetons'])
                stock_quantity = int(data['stock'])
                if jetons < 0 or stock_quantity < 0:
                    api.abort(400, "Les valeurs de jetons et stock doivent être positives")
            except (ValueError, TypeError):
                api.abort(400, "Les valeurs de jetons et stock doivent être des nombres entiers")

            # Gestion sécurisée de l'image (si fournie)
            image_url = None
            
            # Priorité 1: Upload de fichier (si fourni)
            if 'image' in request.files:
                file = request.files['image']
                if file and file.filename != '':
                    if not allowed_file(file.filename):
                        api.abort(400, "Type de fichier non autorisé. Utilisez PNG, JPEG ou GIF")
                    
                    if not validate_file_size(file):
                        api.abort(400, f"Fichier trop volumineux. Taille maximum: {MAX_FILE_SIZE // (1024*1024)}MB")

                    filename = secure_filename(file.filename)
                    timestamp = datetime.utcnow().strftime('%Y%m%d%H%M%S')
                    unique_filename = f"{timestamp}_{filename}"
                    file_path = os.path.join(UPLOAD_FOLDER, unique_filename)
                    file.save(file_path)
                    image_url = f"/{file_path}"
            
            # Priorité 2: URL de récompense (si fournie et pas d'upload)
            elif data.get('recompense_image_url'):
                image_url = data['recompense_image_url']
                # Validation basique de l'URL
                if not image_url.startswith(('http://', 'https://')):
                    api.abort(400, "L'URL de récompense doit commencer par http:// ou https://")

            # Création sécurisée du nouveau stock
            new_stock = MyWittiLot(
                libelle=data['libelle'],
                jetons=jetons,
                stock=stock_quantity,
                recompense_image=image_url,
                category_id=data.get('category_id'),
                created_at=datetime.utcnow()
            )

            db.session.add(new_stock)
            db.session.commit()
            
            return {
                'id': new_stock.id,
                'libelle': new_stock.libelle,
                'jetons': new_stock.jetons,
                'stock': new_stock.stock,
                'recompense_image': new_stock.recompense_image or "",
                'category': new_stock.category.category_name if new_stock.category else "Sans catégorie",
                'created_at': new_stock.created_at.strftime('%Y-%m-%d %H:%M:%S') if new_stock.created_at else "Unknown"
            }, 201

        except IntegrityError as e:
            db.session.rollback()
            api.abort(400, f"Erreur d'intégrité : {str(e)}")
        except Exception as e:
            db.session.rollback()
            api.abort(500, f"Erreur lors de la création du stock: {str(e)}")

class StockDetail(Resource):
    @jwt_required()
    @api.marshal_with(stock_model)
    def put(self, stock_id):
        try:
            # Vérification sécurisée des autorisations super admin
            user_id = get_jwt_identity()
            user = MyWittiUser.query.filter_by(user_id=user_id).first()

            if not user or not user.is_superuser:
                api.abort(403, "Seuls les super admins peuvent modifier le stock")
            
            # Récupération sécurisée du stock
            stock = MyWittiLot.query.get_or_404(stock_id)

            # Récupération et validation des données
            data = request.get_json()
            if not data:
                api.abort(400, "Données JSON requises")

            # Validation des valeurs numériques
            if 'jetons' in data:
                try:
                    jetons = int(data['jetons'])
                    if jetons < 0:
                        api.abort(400, "La valeur de jetons doit être positive")
                    stock.jetons = jetons
                except (ValueError, TypeError):
                    api.abort(400, "La valeur de jetons doit être un nombre entier")

            if 'stock' in data:
                try:
                    stock_quantity = int(data['stock'])
                    if stock_quantity < 0:
                        api.abort(400, "La valeur de stock doit être positive")
                    stock.stock = stock_quantity
                except (ValueError, TypeError):
                    api.abort(400, "La valeur de stock doit être un nombre entier")

            # Mise à jour des autres champs
            if 'libelle' in data:
                stock.libelle = data['libelle']
            if 'category_id' in data:
                stock.category_id = data['category_id']

            # Gestion sécurisée de l'image (si fournie)
            if 'image' in request.files:
                file = request.files['image']
                if file and file.filename != '':
                    if not allowed_file(file.filename):
                        api.abort(400, "Type de fichier non autorisé. Utilisez PNG, JPEG ou GIF")
                    
                    if not validate_file_size(file):
                        api.abort(400, f"Fichier trop volumineux. Taille maximum: {MAX_FILE_SIZE // (1024*1024)}MB")

                    # Suppression sécurisée de l'ancienne image (seulement si c'est un fichier local)
                    if stock.recompense_image and stock.recompense_image.startswith('/static/'):
                        old_file_path = stock.recompense_image.lstrip('/')
                        if os.path.exists(old_file_path):
                            try:
                                os.remove(old_file_path)
                            except OSError:
                                pass  # Ignorer les erreurs de suppression

                    # Sauvegarde de la nouvelle image
                    filename = secure_filename(file.filename)
                    timestamp = datetime.utcnow().strftime('%Y%m%d%H%M%S')
                    unique_filename = f"{timestamp}_{filename}"
                    file_path = os.path.join(UPLOAD_FOLDER, unique_filename)
                    file.save(file_path)
                    stock.recompense_image = f"/{file_path}"
            
            # Mise à jour avec URL de récompense (si fournie)
            elif data.get('recompense_image_url'):
                # Suppression sécurisée de l'ancienne image (seulement si c'est un fichier local)
                if stock.recompense_image and stock.recompense_image.startswith('/static/'):
                    old_file_path = stock.recompense_image.lstrip('/')
                    if os.path.exists(old_file_path):
                        try:
                            os.remove(old_file_path)
                        except OSError:
                            pass  # Ignorer les erreurs de suppression
                
                # Validation de l'URL
                image_url = data['recompense_image_url']
                if not image_url.startswith(('http://', 'https://')):
                    api.abort(400, "L'URL de récompense doit commencer par http:// ou https://")
                
                stock.recompense_image = image_url

            stock.updated_at = datetime.utcnow()
            db.session.commit()
            
            return {
                'id': stock.id,
                'libelle': stock.libelle or "Sans titre",
                'jetons': stock.jetons or 0,
                'stock': stock.stock or 0,
                'recompense_image': stock.recompense_image or "",
                'category': stock.category.category_name if stock.category else "Sans catégorie",
                'created_at': stock.created_at.strftime('%Y-%m-%d %H:%M:%S') if stock.created_at else "Date inconnue"
            }

        except Exception as e:
            db.session.rollback()
            api.abort(500, f"Erreur lors de la modification du stock: {str(e)}")

    @jwt_required()
    def delete(self, stock_id):
        try:
            # Vérification sécurisée des autorisations super admin
            user_id = get_jwt_identity()
            user = MyWittiUser.query.filter_by(user_id=user_id).first()

            if not user or not user.is_superuser:
                api.abort(403, "Seuls les super admins peuvent supprimer le stock")
            
            # Récupération sécurisée du stock
            stock = MyWittiLot.query.get_or_404(stock_id)
            
            # Vérification si le stock a des commandes en cours
            pending_orders = db.session.query(MyWittiLotsClaims).filter_by(
                lot_id=stock.id, 
                statut='pending'
            ).count()
            
            if pending_orders > 0:
                api.abort(400, f"Impossible de supprimer le stock. Il a {pending_orders} commande(s) en attente.")

            # Suppression sécurisée de l'image associée (seulement si c'est un fichier local)
            if stock.recompense_image and stock.recompense_image.startswith('/static/'):
                file_path = stock.recompense_image.lstrip('/')
                if os.path.exists(file_path):
                    try:
                        os.remove(file_path)
                    except OSError:
                        pass  # Ignorer les erreurs de suppression

            db.session.delete(stock)
            db.session.commit()
            return {"message": "Stock supprimé avec succès"}, 200

        except Exception as e:
            db.session.rollback()
            api.abort(500, f"Erreur lors de la suppression du stock: {str(e)}")