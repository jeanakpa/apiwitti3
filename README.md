# Witti_Witti API

API REST pour l'application Witti_Witti avec authentification JWT et gestion des utilisateurs, clients, sondages, FAQ et support.

## 🚀 Installation

### Prérequis
- Python 3.8+
- PostgreSQL
- pip

### Configuration

1. **Cloner le projet**
```bash
git clone <repository-url>
cd Witti_Witti
```

2. **Installer les dépendances**
```bash
pip install -r requirements.txt
```

3. **Configuration des variables d'environnement**
```bash
# Copier le fichier d'exemple
cp env_example.txt .env

# Éditer le fichier .env avec vos valeurs
# Variables OBLIGATOIRES :
SECRET_KEY=your-secret-key-here
JWT_SECRET_KEY=your-jwt-secret-key-here
DATABASE_URL=postgresql://username:password@localhost:5432/database_name
```

4. **Configuration de la base de données**
```bash
# Créer la base de données PostgreSQL
createdb witti

# Exécuter les migrations
flask db upgrade
```

5. **Lancer l'application**
```bash
# Mode développement
export FLASK_ENV=development
python app.py

# Mode production
export FLASK_ENV=production
python app.py
```

## 🔧 Configuration

### Variables d'environnement

| Variable | Description | Obligatoire | Défaut |
|----------|-------------|-------------|---------|
| `SECRET_KEY` | Clé secrète Flask | ✅ | - |
| `JWT_SECRET_KEY` | Clé secrète JWT | ✅ | - |
| `DATABASE_URL` | URL de connexion PostgreSQL | ✅ | - |
| `CORS_ORIGINS` | Origines CORS autorisées | ❌ | * |
| `SUPPORT_PHONE` | Téléphone support | ❌ | +2250710922213 |
| `SUPPORT_EMAIL` | Email support | ❌ | misterjohn0798@gmail.com |
| `LOG_LEVEL` | Niveau de logging | ❌ | INFO |
| `FLASK_ENV` | Environnement Flask | ❌ | development |

### Environnements

- **Development** : Mode debug activé, logs détaillés
- **Production** : Mode debug désactivé, validation stricte des variables d'environnement
- **Testing** : Base de données en mémoire pour les tests

## 📚 API Endpoints

### Authentification
- `POST /accounts/login` - Connexion utilisateur
- `POST /accounts/admin/login` - Connexion admin
- `POST /customer/logout` - Déconnexion client
- `POST /admin/logout` - Déconnexion admin

### Clients
- `GET /customer/{customer_code}/dashboard` - Tableau de bord client
- `GET /customer/{customer_code}/transactions` - Historique des transactions
- `GET /customer/{customer_code}/profile` - Profil client
- `GET /customer/{customer_code}/notifications` - Notifications client

### FAQ
- `GET /faq` - Liste des FAQ

### Sondages
- `GET /survey/surveys` - Liste des sondages actifs
- `POST /survey/surveys/{survey_id}/respond` - Répondre à un sondage

### Support
- `GET /support/contact` - Informations de contact support
- `POST /support/request` - Soumettre une demande de support

### Admin (Authentification requise)
- `GET /admin/customers` - Liste des clients
- `POST /admin/customers` - Créer un client
- `PUT /admin/customers` - Modifier un client
- `GET /admin/orders` - Liste des commandes
- `PUT /admin/orders/{order_id}/validate` - Valider une commande
- `GET /admin/stock` - Gestion du stock
- `POST /admin/stock` - Ajouter du stock
- `GET /admin/surveys` - Gestion des sondages
- `POST /admin/surveys` - Créer un sondage

## 🔒 Sécurité

### Authentification JWT
- Tokens d'accès valides 24h
- Tokens de rafraîchissement valides 30 jours
- Blacklist des tokens révoqués

### Validation des données
- Validation des champs requis
- Sanitisation des entrées utilisateur
- Validation des formats (email, téléphone)
- Limitation de taille des fichiers uploadés

### Gestion des erreurs
- Gestion cohérente des erreurs HTTP
- Logs détaillés pour le debugging
- Messages d'erreur sécurisés (pas d'exposition d'informations sensibles)

## 🛠️ Améliorations apportées

### 1. Sécurité
- ✅ Suppression des clés secrètes hardcodées
- ✅ Configuration par variables d'environnement
- ✅ Validation et sanitisation des entrées
- ✅ Gestion sécurisée des uploads de fichiers

### 2. Gestion d'erreurs
- ✅ Gestionnaires d'erreurs globaux
- ✅ Format de réponse standardisé
- ✅ Logs structurés et appropriés
- ✅ Rollback automatique des sessions DB

### 3. Configuration
- ✅ Configuration par environnement (dev/prod/test)
- ✅ Variables d'environnement obligatoires
- ✅ Configuration CORS flexible
- ✅ Limitation de taille des fichiers

### 4. Code
- ✅ Suppression du code dupliqué
- ✅ Utilitaires de validation réutilisables
- ✅ Décorateurs pour la gestion d'erreurs
- ✅ Documentation des endpoints

## 📝 Logs

Les logs sont configurés avec différents niveaux :
- **INFO** : Opérations normales
- **WARNING** : Problèmes non critiques
- **ERROR** : Erreurs nécessitant attention
- **DEBUG** : Informations détaillées (mode développement uniquement)

## 🧪 Tests

Pour exécuter les tests :
```bash
export FLASK_ENV=testing
python -m pytest
```

## 📦 Déploiement

### Production
1. Configurer les variables d'environnement de production
2. Utiliser un serveur WSGI (Gunicorn, uWSGI)
3. Configurer un reverse proxy (Nginx)
4. Activer HTTPS
5. Configurer la rotation des logs

### Docker (optionnel)
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "app.py"]
```

## 🤝 Contribution

1. Fork le projet
2. Créer une branche feature (`git checkout -b feature/AmazingFeature`)
3. Commit les changements (`git commit -m 'Add some AmazingFeature'`)
4. Push vers la branche (`git push origin feature/AmazingFeature`)
5. Ouvrir une Pull Request

## 📄 Licence

Ce projet est sous licence MIT. Voir le fichier `LICENSE` pour plus de détails. 