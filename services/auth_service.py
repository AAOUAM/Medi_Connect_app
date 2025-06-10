import bcrypt
from datetime import datetime
from bson import ObjectId
from functools import wraps
from flask import session, request, redirect, url_for, flash
from services.mongo_service import get_utilisateur_by_email , get_utilisateur_by_id , insert_utilisateur , get_medecin_by_nom , get_patient_by_nom

class AuthService:

    @staticmethod
    def hash_password(password: str) -> str:
        hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        return hashed.decode('utf-8')  # Stockage en string (UTF-8)

    @staticmethod
    def verify_password(password: str, hashed_password) -> bool:
        if isinstance(hashed_password, str):
            hashed_password = hashed_password.encode('utf-8')
        return bcrypt.checkpw(password.encode('utf-8'), hashed_password)

    @staticmethod
    def create_user(email, password, role, nom=None ):

        # Vérifier si l'utilisateur existe déjà
        if get_utilisateur_by_email(email):
            return {"success": False, "message": "Cet email existe déjà"}

        # Hasher le mot de passe
        hashed_password = AuthService.hash_password(password)

        if role == 'medecin':
            user = get_medecin_by_nom(nom)
        elif role == 'patient':
            user = get_patient_by_nom(nom)
        else:
            user = None

            
        # Créer l'utilisateur
        user_data = {
            'id_fonctionnel': user['_id'] if user else None,
            "email": email,
            "mot_de_passe": hashed_password,
            "role": role,
            "date_creation": datetime.now()
        }

        # Ajouter nom et prénom si fournis
        if nom:
            user_data["nom"] = nom

        try:
            result = insert_utilisateur(user_data)
            return {
                "success": True,
                "message": "Utilisateur créé avec succès",
                "user_id": str(result.inserted_id)
            }
        except Exception as e:
            return {"success": False, "message": f"Erreur lors de la création: {str(e)}"}

    @staticmethod
    def authenticate_user(email, password):
        """Authentifier un utilisateur"""

        # Trouver l'utilisateur
        user = get_utilisateur_by_email(email)

        if not user:
            return {"success": False, "message": "Email ou mot de passe incorrect"}

        # Vérifier le mot de passe
        if AuthService.verify_password(password, user["mot_de_passe"]):
            return {
                "success": True,
                "user": {
                    "id": str(user["_id"]),
                    "email": user["email"],
                    "role": user["role"],
                    "nom": user.get("nom", ""),
                    "id_fonctionnel" : user.get("id_fonctionnel", None)
                }
            }
        else:
            return {"success": False, "message": "Email ou mot de passe incorrect"}

    @staticmethod
    def get_user_by_id(user_id):
        """Récupérer un utilisateur par son ID"""
        try:
            user = get_utilisateur_by_id({"_id": ObjectId(user_id)})
            if user:
                return {
                    "id": str(user["_id"]),
                    "email": user["email"],
                    "role": user["role"],
                    "nom": user.get("nom", "")
                }
        except:
            pass
        return None

# Décorateurs pour protéger les routes
def login_required(f):
    """Décorateur pour exiger une connexion"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Vous devez être connecté pour accéder à cette page', 'error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def role_required(required_roles):
    """Décorateur pour exiger un rôle spécifique"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session:
                flash('Vous devez être connecté', 'error')
                return redirect(url_for('login'))

            user = AuthService.get_user_by_id(session['user_id'])
            if not user or user['role'] not in required_roles:
                flash('Vous n\'avez pas les permissions nécessaires', 'error')
                return redirect(url_for('login'))

            return f(*args, **kwargs)
        return decorated_function
    return decorator

def admin_required(f):
    """Décorateur pour exiger le rôle admin"""
    return role_required(['admin'])(f)

def medecin_required(f):
    """Décorateur pour exiger le rôle médecin ou admin"""
    return role_required(['medecin'])(f)

def patient_required(f):
    """Décorateur pour exiger le rôle patient ou admin"""
    return role_required(['patient'])(f)