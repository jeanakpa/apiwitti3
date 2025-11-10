# Guide de Déploiement - Witti Witti API

## 🚀 Déploiement sur Render

### Prérequis

1. **Compte Render** : Créez un compte sur [render.com](https://render.com)
2. **Base de données PostgreSQL** : Configurez une base de données PostgreSQL sur Render
3. **Variables d'environnement** : Préparez vos variables d'environnement

### Variables d'environnement requises

Configurez ces variables dans votre service Render :

```bash
# Clés de sécurité (obligatoires)
SECRET_KEY=votre_secret_key_tres_longue_et_complexe
JWT_SECRET_KEY=votre_jwt_secret_key_tres_longue_et_complexe

# Base de données (obligatoire)
DATABASE_URL=postgresql://username:password@host:port/database

# Configuration (optionnelles)
FLASK_ENV=production
CORS_ORIGINS=https://votre-frontend.com,https://autre-domaine.com
LOG_LEVEL=INFO

# Support (optionnelles)
SUPPORT_PHONE=+2250710922213
SUPPORT_WHATSAPP=+2250710922213
SUPPORT_EMAIL=misterjohn0798@gmail.com
```

### Étapes de déploiement

1. **Connectez votre repository GitHub** à Render
2. **Créez un nouveau Web Service**
3. **Configurez le service** :
   - **Build Command** : `pip install -r requirements.txt`
   - **Start Command** : `gunicorn wsgi:app`
   - **Environment** : Python 3.13

### Structure des fichiers

```
Witti_Witti/
├── app.py                 # Application principale
├── wsgi.py               # Point d'entrée WSGI
├── config.py             # Configuration
├── requirements.txt      # Dépendances Python
├── runtime.txt          # Version Python
├── render.yaml          # Configuration Render
├── .gitignore           # Fichiers à ignorer
├── Models/              # Modèles de données
│   ├── __init__.py
│   ├── mywitti_survey.py
│   ├── mywitti_users.py
│   └── ...
├── Account/             # API Comptes
│   ├── __init__.py
│   └── views.py
├── Customer/            # API Clients
│   ├── __init__.py
│   └── views.py
├── Admin/               # API Admin
│   ├── __init__.py
│   └── views.py
└── ...
```

### Test local avant déploiement

```bash
# Installer les dépendances
pip install -r requirements.txt

# Tester les imports
python test_deployment.py

# Tester l'application
python wsgi.py
```

### Endpoints disponibles après déploiement

- **Documentation API** : `https://votre-app.onrender.com/`
- **Comptes** : `https://votre-app.onrender.com/accounts/`
- **Clients** : `https://votre-app.onrender.com/customer/`
- **Admin** : `https://votre-app.onrender.com/admin/`
- **Publicités** : `https://votre-app.onrender.com/advertisement/`
- **Lots** : `https://votre-app.onrender.com/lot/`
- **FAQ** : `https://votre-app.onrender.com/faq/`
- **Support** : `https://votre-app.onrender.com/support/`
- **Sondages** : `https://votre-app.onrender.com/survey/`

### Dépannage

#### Erreur "ModuleNotFoundError"

Si vous obtenez une erreur `ModuleNotFoundError: No module named 'Models.mywitti_survey'` :

1. Vérifiez que tous les dossiers ont un fichier `__init__.py`
2. Vérifiez que le fichier `mywitti_survey.py` existe dans le dossier `Models/`
3. Testez localement avec `python test_deployment.py`

#### Erreur de base de données

1. Vérifiez que `DATABASE_URL` est correctement configuré
2. Vérifiez que la base de données PostgreSQL est accessible
3. Vérifiez que les tables existent (exécutez les migrations si nécessaire)

#### Erreur de variables d'environnement

1. Vérifiez que `SECRET_KEY` et `JWT_SECRET_KEY` sont définis
2. Vérifiez que `DATABASE_URL` est défini en production

### Commandes utiles

```bash
# Tester localement
python test_deployment.py

# Démarrer en mode développement
python app.py

# Démarrer avec Gunicorn (production)
gunicorn wsgi:app

# Vérifier les logs Render
# Utilisez l'interface web de Render pour voir les logs
```

### Support

En cas de problème :
1. Vérifiez les logs dans l'interface Render
2. Testez localement avec `python test_deployment.py`
3. Vérifiez que toutes les variables d'environnement sont configurées
4. Contactez le support technique si nécessaire 