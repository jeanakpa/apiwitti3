import os
from datetime import timedelta

class Config:
    # Configuration de base
    SECRET_KEY = os.environ.get('SECRET_KEY')
    if not SECRET_KEY:
        raise ValueError("SECRET_KEY environment variable is required")
    
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY')
    if not JWT_SECRET_KEY:
        raise ValueError("JWT_SECRET_KEY environment variable is required")
    
    # Configuration de la base de données
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Configuration JWT
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=24)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    
    # Configuration CORS
    CORS_ORIGINS = os.environ.get('CORS_ORIGINS', '*').split(',')
    
    # Configuration du support
    SUPPORT_PHONE = os.environ.get('SUPPORT_PHONE', '+2250710922213')
    SUPPORT_WHATSAPP = os.environ.get('SUPPORT_WHATSAPP', '+2250710922213')
    SUPPORT_EMAIL = os.environ.get('SUPPORT_EMAIL', 'misterjohn0798@gmail.com')
    WHATSAPP_DEFAULT_MESSAGE = os.environ.get('WHATSAPP_DEFAULT_MESSAGE', 'Bonjour, j''ai besoin d''aide avec l''application.')
    
    # Configuration des uploads
    UPLOAD_FOLDER = 'static/uploads'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    
    # Configuration des logs
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
    
    # Liste des pays
    COUNTRY_LIST = {
        1: "Côte d'Ivoire",
        2: "Burkina Faso",
        3: "Sénégal"
    }

class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    # Utiliser SQLite en développement pour faciliter les tests
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///mywitti.db'

class ProductionConfig(Config):
    DEBUG = False
    # En production, forcer l'utilisation de variables d'environnement
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    if not SQLALCHEMY_DATABASE_URI:
        raise ValueError("DATABASE_URL environment variable is required in production")

class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'

# Configuration par défaut selon l'environnement
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
