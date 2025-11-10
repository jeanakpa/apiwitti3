#!/bin/bash
# Script de démarrage pour Render

echo "🚀 Démarrage de l'application Witti Witti API..."

# Configuration du PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Vérification des variables d'environnement
echo "📋 Vérification des variables d'environnement..."
if [ -z "$SECRET_KEY" ]; then
    echo "❌ SECRET_KEY non définie"
    exit 1
fi

if [ -z "$JWT_SECRET_KEY" ]; then
    echo "❌ JWT_SECRET_KEY non définie"
    exit 1
fi

if [ -z "$DATABASE_URL" ]; then
    echo "❌ DATABASE_URL non définie"
    exit 1
fi

echo "✅ Variables d'environnement configurées"

# Vérification de la structure des fichiers
echo "📁 Vérification de la structure des fichiers..."
if [ ! -f "wsgi.py" ]; then
    echo "❌ wsgi.py non trouvé"
    exit 1
fi

if [ ! -f "app.py" ]; then
    echo "❌ app.py non trouvé"
    exit 1
fi

if [ ! -d "Models" ]; then
    echo "❌ Dossier Models non trouvé"
    exit 1
fi

echo "✅ Structure des fichiers correcte"

# Test d'import Python
echo "🐍 Test d'import Python..."
python3 -c "
import sys
sys.path.insert(0, '.')
try:
    from Models.mywitti_survey import MyWittiSurvey
    print('✅ Import Models.mywitti_survey réussi')
except ImportError as e:
    print(f'❌ Erreur d\'import: {e}')
    sys.exit(1)
"

if [ $? -ne 0 ]; then
    echo "❌ Test d'import échoué"
    exit 1
fi

# Démarrage de Gunicorn
echo "🚀 Démarrage de Gunicorn..."
exec gunicorn wsgi:app --bind 0.0.0.0:$PORT --timeout 120 --workers 1 