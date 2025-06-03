from pymongo import MongoClient
from bson.objectid import ObjectId
from datetime import datetime, timedelta 
from config import MONGO_URI, MONGO_DB


client = MongoClient(MONGO_URI)
db = client[MONGO_DB]

# Vérification de la connexion (optionnelle mais recommandée à l'initialisation)
try:
    client.admin.command('ping')
    print(f"Connecté avec succès à MongoDB: {MONGO_DB} sur {MONGO_URI}")
except Exception as e:
    print(f"Erreur de connexion à MongoDB: {e}")




# === PATIENTS ( CRUD ) ===

def insert_patient(patient_data):
    """Créer un patient"""
    return db.patients.insert_one(patient_data)

def get_all_patients():
    """Lire tous les patients"""
    return list(db.patients.find())

def get_patient_by_id(patient_id_str): 
    """Lire un patient par ID (chaîne)"""
    try:
        return db.patients.find_one({"_id": ObjectId(patient_id_str)})
    except Exception as e: # Gérer les erreurs de conversion d'ObjectId
        print(f"Erreur ObjectId pour patient_id {patient_id_str}: {e}")
        return None

def update_patient(patient_id_str, updated_data): 
    """Mettre à jour un patient"""
    try:
        return db.patients.update_one({"_id": ObjectId(patient_id_str)}, {"$set": updated_data})
    except Exception as e:
        print(f"Erreur ObjectId pour patient_id {patient_id_str} lors de la mise à jour: {e}")
        return None


def delete_patient(patient_id_str): 
    """Supprimer un patient"""
    try:
        return db.patients.delete_one({"_id": ObjectId(patient_id_str)})
    except Exception as e:
        print(f"Erreur ObjectId pour patient_id {patient_id_str} lors de la suppression: {e}")
        return None





# === MEDECINS ( CRUD ) ===

def insert_medecin(medecin_data):
    """Créer un médecin"""
    return db.medecins.insert_one(medecin_data)

def get_all_medecins():
    """Lire tous les médecins"""
    return list(db.medecins.find())

def get_medecin_by_id(medecin_id_str): # Renommé
    """Lire un médecin par ID (chaîne)"""
    try:
        return db.medecins.find_one({"_id": ObjectId(medecin_id_str)})
    except Exception as e:
        print(f"Erreur ObjectId pour medecin_id {medecin_id_str}: {e}")
        return None

def update_medecin(medecin_id_str, updated_data): # Renommé
    """Mettre à jour un médecin"""
    try:
        return db.medecins.update_one({"_id": ObjectId(medecin_id_str)}, {"$set": updated_data})
    except Exception as e:
        print(f"Erreur ObjectId pour medecin_id {medecin_id_str} lors de la mise à jour: {e}")
        return None

def delete_medecin(medecin_id_str): # Renommé
    """Supprimer un médecin"""
    try:
        return db.medecins.delete_one({"_id": ObjectId(medecin_id_str)})
    except Exception as e:
        print(f"Erreur ObjectId pour medecin_id {medecin_id_str} lors de la suppression: {e}")
        return None






# === CONSULTATIONS ===


def insert_consultation(consultation_data):
    """Créer une consultation"""
    # Assurez-vous que id_patient et id_medecin sont des ObjectId si stockés ainsi
    if 'id_patient' in consultation_data and isinstance(consultation_data['id_patient'], str):
        try:
            consultation_data['id_patient'] = ObjectId(consultation_data['id_patient'])
        except: pass # Laisser tel quel si ce n'est pas un format ObjectId valide
    if 'id_medecin' in consultation_data and isinstance(consultation_data['id_medecin'], str):
        try:
            consultation_data['id_medecin'] = ObjectId(consultation_data['id_medecin'])
        except: pass
    return db.consultations.insert_one(consultation_data)


def get_consultation_by_id(consultation_id_str):
    """Lire une consultation par ID (chaîne)"""
    try:
        return db.consultations.find_one({"_id": ObjectId(consultation_id_str)})
    except Exception as e:
        print(f"Erreur ObjectId pour consultation_id {consultation_id_str}: {e}")
        return None


def get_all_consultations():
    """Lire toutes les consultations (simple find)"""
    return list(db.consultations.find())




# # === UTILISATEURS ===

# def insert_user(user_data):
#     """Créer un utilisateur"""
#     # Pensez à hasher le mot de passe ici avant insertion !
#     # from werkzeug.security import generate_password_hash
#     # if 'password' in user_data:
#     #     user_data['password'] = generate_password_hash(user_data['password'])
#     return db.utilisateurs.insert_one(user_data)

# def get_user_by_username(username):
#     """Trouver un utilisateur par son nom d'utilisateur"""
#     return db.utilisateurs.find_one({"username": username}) # Ou "email" selon votre modèle

# def get_user_by_id(user_id_str):
#     """Trouver un utilisateur par son ID (chaîne)"""
#     try:
#         return db.utilisateurs.find_one({"_id": ObjectId(user_id_str)})
#     except Exception as e:
#         print(f"Erreur ObjectId pour user_id {user_id_str}: {e}")
#         return None

# def get_all_users():
#     """Lire tous les utilisateurs"""
#     return list(db.utilisateurs.find())



# === FONCTIONS SPÉCIFIQUES AU TABLEAU DE BORD (Intégration) ===

def count_patients():
    """Compte le nombre total de patients."""
    return db.patients.count_documents({})

def count_medecins():
    """Compte le nombre total de médecins."""
    return db.medecins.count_documents({})

def count_consultations():
    """Compte le nombre total de consultations."""
    return db.consultations.count_documents({})

def count_users():
    """Compte le nombre total d'utilisateurs."""
    return db.utilisateurs.count_documents({})


def get_recent_consultations_with_details(limit=5):
    """
    Récupère les consultations récentes de MongoDB avec les noms de patient/médecin via $lookup.
    Utilise le champ 'date' (chaîne YYYY-MM-DD) pour le tri.
    """
    consultations_coll = db.consultations # Utilise l'objet db global
    
    pipeline = [
        {"$sort": {"date": -1}}, # Tri par date (chaîne) descendante
        {"$limit": limit},
        {
            "$lookup": {
                "from": "patients",
                "localField": "id_patient", # Doit être ObjectId dans 'consultations'
                "foreignField": "_id",     # Doit être ObjectId dans 'patients'
                "as": "patient_info_array" # Renommé pour éviter conflit avec $unwind si le champ existe déjà
            }
        },
        {
            "$unwind": {
                "path": "$patient_info_array",
                "preserveNullAndEmptyArrays": True
            }
        },
        {
            "$lookup": {
                "from": "medecins",
                "localField": "id_medecin", # Doit être ObjectId dans 'consultations'
                "foreignField": "_id",     # Doit être ObjectId dans 'medecins'
                "as": "medecin_info_array"
            }
        },
        {
            "$unwind": {
                "path": "$medecin_info_array",
                "preserveNullAndEmptyArrays": True
            }
        },
        {
            "$project": {
                "_id": 1,
                "nom_patient": {
                    "$ifNull": [ # Gère le cas où patient_info_array ou ses champs sont null
                        {"$concat": ["$patient_info_array.prenom", " ", "$patient_info_array.nom"]},
                        "Patient Inconnu"
                    ]
                },
                "nom_medecin": {
                    "$ifNull": [
                        {"$concat": ["Dr. ", "$medecin_info_array.prenom", " ", "$medecin_info_array.nom"]},
                        "Médecin Inconnu"
                    ]
                },
                "date_consultation_str": "$date", # La date est déjà une chaîne
                "diagnostic": {"$ifNull": ["$diagnostic", "N/A"]},
            }
        }
    ]
    
    formatted_consultations = []
    try:
        raw_consultations = list(consultations_coll.aggregate(pipeline))
        for consult in raw_consultations:
            # Convertir la date YYYY-MM-DD en DD/MM/YYYY pour l'affichage si besoin
            date_str = consult.get("date_consultation_str", "Date Inconnue")
            try:
                date_obj = datetime.strptime(date_str, "%Y-%m-%d")
                display_date = date_obj.strftime("%d/%m/%Y")
            except (ValueError, TypeError):
                display_date = date_str # Garder la chaîne si format incorrect ou None

            formatted_consultations.append({
                "id": str(consult["_id"]),
                "nom_patient": consult.get("nom_patient"),
                "nom_medecin": consult.get("nom_medecin"),
                "date": display_date,
                "diagnostic": consult.get("diagnostic")
            })
    except Exception as e:
        print(f"Erreur lors de la récupération des consultations récentes avec détails: {e}")
    return formatted_consultations


def get_monthly_consultation_stats():
    """Calcule les statistiques mensuelles de consultations."""
    consultations_coll = db.consultations

    today = datetime.utcnow()
    # Date de début: premier jour du mois, il y a 11 mois (pour avoir 12 mois au total incluant le mois courant)
    # Pour une période de 12 mois se terminant le mois dernier + le mois courant
    start_date_for_labels = (today.replace(day=1) - timedelta(days=335)).replace(day=1) # Approche pour 12 mois de labels
    end_date_for_labels = today # Jusqu'à aujourd'hui pour les labels

    pipeline = [
        {
            "$addFields": { # Convertir la chaîne de date en objet Date pour l'agrégation
                "date_obj_for_aggregation": {
                    "$dateFromString": {
                        "dateString": "$date", # Votre champ date est une chaîne "YYYY-MM-DD"
                        "format": "%Y-%m-%d",
                        "onError": None # Important pour filtrer les dates invalides
                    }
                }
            }
        },
        {
            "$match": { # Filtrer les dates converties valides et dans une plage (ex: 2 dernières années)
                "date_obj_for_aggregation": {
                    "$ne": None, # Exclure celles où la conversion a échoué
                    # Optionnel: ajouter un filtre de plage pour la performance si beaucoup de données anciennes
                    # "$gte": datetime(today.year - 2, 1, 1) 
                }
            }
        },
        {
            "$group": {
                "_id": {
                    "year": {"$year": "$date_obj_for_aggregation"},
                    "month": {"$month": "$date_obj_for_aggregation"}
                },
                "count": {"$sum": 1}
            }
        },
        {
            "$sort": {"_id.year": 1, "_id.month": 1} # Trier par date
        },
        {
            "$project": { # Reformater la sortie
                "_id": 0,
                "label": { # Créer un label "MM-YYYY"
                    "$concat": [
                        {"$cond": [{"$lt": ["$_id.month", 10]}, {"$concat": ["0", {"$toString": "$_id.month"}]}, {"$toString": "$_id.month"}]},
                        "-",
                        {"$toString": "$_id.year"}
                    ]
                },
                "value": "$count"
            }
        }
    ]
    
    aggregated_results = []
    try:
        aggregated_results = list(consultations_coll.aggregate(pipeline))
    except Exception as e:
        print(f"Erreur lors de l'agrégation des statistiques mensuelles: {e}")

    # Générer les labels pour les 12 derniers mois (incluant le mois courant)
    # pour s'assurer que tous les mois sont présents, même avec 0 consultation.
    all_months_labels = []
    # Commence au premier jour du mois, il y a 11 mois
    current_month_iter = (datetime(today.year, today.month, 1) - timedelta(days=335)).replace(day=1) 
    for _ in range(12): # Générer 12 labels de mois
        all_months_labels.append(current_month_iter.strftime("%m-%Y"))
        # Passer au mois suivant (méthode robuste)
        if current_month_iter.month == 12:
            current_month_iter = current_month_iter.replace(year=current_month_iter.year + 1, month=1)
        else:
            current_month_iter = current_month_iter.replace(month=current_month_iter.month + 1)
    
    data_map = {item['label']: item['value'] for item in aggregated_results}
    final_data_values = [data_map.get(label, 0) for label in all_months_labels]

    return {"labels": all_months_labels, "data": final_data_values}