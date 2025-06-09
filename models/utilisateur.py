from services.mongo_service import (
    insert_utilisateur, get_utilisateur_by_email,
    get_utilisateur_by_id , update_utilisateur, delete_utilisateur
)

from datetime import datetime
import bcrypt

def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

def verify_password(password, hashed):
    return bcrypt.checkpw(password.encode('utf-8'), hashed)

def create_utilisateur(data):
    existing = get_utilisateur_by_email(data["email"])
    if existing:
        raise ValueError("Un utilisateur avec cet email existe déjà.")

    utilisateur = {
        "email": data["email"],
        "mot_de_passe": hash_password(data["mot_de_passe"]),
        "role": data.get("role", "patient"),
        "date_creation": datetime.utcnow().isoformat()
    }
    result = insert_utilisateur(utilisateur)
    return str(result.inserted_id)

def authenticate_utilisateur(email, password):
    utilisateur = get_utilisateur_by_email(email)
    if utilisateur and verify_password(password, utilisateur["mot_de_passe"]):
        return utilisateur
    return None

def retrieve_utilisateur_by_id(utilisateur_id):
    return get_utilisateur_by_id(utilisateur_id)

def modify_utilisateur(utilisateur_id, updated_data):
    if "mot_de_passe" in updated_data:
        updated_data["mot_de_passe"] = hash_password(updated_data["mot_de_passe"])
    update_utilisateur(utilisateur_id, updated_data)

def delete_utilisateur_record(utilisateur_id):
    delete_utilisateur(utilisateur_id)
