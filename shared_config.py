# shared_config.py

# Dictionnaire simulant la configuration partagée
CUSTOMER_COUNTRIES = {}

def set_customer_country(customer_id, country):
    """Enregistre le pays d’un client donné."""
    CUSTOMER_COUNTRIES[customer_id] = country
    print(f"[shared_config] Pays du client {customer_id} défini sur {country}")

def get_user_country(customer_id):
    """Retourne le pays enregistré pour un client, ou None s’il n’est pas défini."""
    return CUSTOMER_COUNTRIES.get(customer_id)
