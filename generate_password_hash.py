#!/usr/bin/env python3
"""
Script pour générer les mots de passe hashés pour les utilisateurs de test
"""
from werkzeug.security import generate_password_hash

def generate_hashed_password():
    """Génère le hash du mot de passe '123456'"""
    password = "123456"
    hashed_password = generate_password_hash(password)
    
    print("=== MOT DE PASSE HASHÉ ===")
    print(f"Mot de passe original: {password}")
    print(f"Mot de passe hashé: {hashed_password}")
    print("\n=== INSTRUCTIONS ===")
    print("1. Copiez le hash ci-dessus")
    print("2. Remplacez 'YOUR_HASH_HERE' dans le fichier create_test_data.sql")
    print("3. Exécutez le script SQL dans PostgreSQL")
    
    return hashed_password

if __name__ == "__main__":
    generate_hashed_password() 