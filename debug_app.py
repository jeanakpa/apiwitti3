import os
import logging
from app import create_app

# Configuration des logs détaillés
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Variables d'environnement
os.environ['SECRET_KEY'] = 'dev-secret-key-123'
os.environ['JWT_SECRET_KEY'] = 'dev-jwt-secret-123'
os.environ['DATABASE_URL'] = 'postgresql://postgres:mywitti@localhost:5432/mywitti'

# Création de l'application
app = create_app('development')

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5000) 