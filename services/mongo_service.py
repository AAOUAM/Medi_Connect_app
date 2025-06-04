from pymongo import MongoClient
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash
from datetime import datetime, timedelta 
from config import MONGO_URI, MONGO_DB


client = MongoClient(MONGO_URI)
db = client[MONGO_DB]



# === PATIENTS ( CRUD ) ===

def get_all_patients():
    return list(db.patients.find())

def get_patient_by_id(patient_id_str): 
    return db.patients.find_one({"_id": ObjectId(patient_id_str)})

def insert_patient(patient_data):
    return db.patients.insert_one(patient_data)

def update_patient(patient_id_str, updated_data): 
    return db.patients.update_one({"_id": ObjectId(patient_id_str)}, {"$set": updated_data})

def delete_patient(patient_id_str): 
    return db.patients.delete_one({"_id": ObjectId(patient_id_str)})






# === MEDECINS ( CRUD ) ===

def get_medecin_by_id(medecin_id_str): 
    return db.medecins.find_one({"_id": ObjectId(medecin_id_str)})

def get_all_medecins():
    return list(db.medecins.find())

def insert_medecin(medecin_data):
    return db.medecins.insert_one(medecin_data)


def update_medecin(medecin_id_str, updated_data): 
    return db.medecins.update_one({"_id": ObjectId(medecin_id_str)}, {"$set": updated_data})
    

def delete_medecin(medecin_id_str):
    return db.medecins.delete_one({"_id": ObjectId(medecin_id_str)})
    






# === CONSULTATIONS ===

def get_consultation_by_id(consultation_id_str):
    return db.consultations.find_one({"_id": ObjectId(consultation_id_str)})


def get_all_consultations():
    return list(db.consultations.find())



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





# # === UTILISATEURS ===

def insert_utilisateur(user_data):
    """Créer un utilisateur"""
    if 'password' in user_data:
        user_data['password'] = generate_password_hash(user_data['password'])
    return db.utilisateurs.insert_one(user_data)

def get_utilisateur_by_email(email):
    return db.utilisateurs.find_one({"email": email}) 

def get_utilisateur_by_id(user_id_str):
    return db.utilisateurs.find_one({"_id": ObjectId(user_id_str)})

def get_all_users():
    return list(db.utilisateurs.find())

def delete_utilisateur(user_id_str):
    result = db.utilisateurs.delete_one({"_id": ObjectId(user_id_str)})
    return result.deleted_count  # Retourne 1 si suppression réussie, 0 sinon

def update_utilisateur(user_id_str, update_data):
    """
    Met à jour un utilisateur par son _id.
    Si 'password' est présent dans update_data, on le hash avant.
    """
    if 'password' in update_data:
        update_data['password'] = generate_password_hash(update_data['password'])
    result = db.utilisateurs.update_one(
        {"_id": ObjectId(user_id_str)},
        {"$set": update_data}
    )
    return result.modified_count  # Retourne 1 si mise à jour réussie, 0 sinon



# === FONCTIONS SPÉCIFIQUES AU TABLEAU DE BORD (Intégration) ===

def count_patients():
    return db.patients.count_documents({})

def count_medecins():
    return db.medecins.count_documents({})

def count_consultations():
    return db.consultations.count_documents({})

def count_users():
    return db.utilisateurs.count_documents({})


def get_recent_consultations_with_details(limit=5):
    consultations_coll = db.consultations
    patients_coll = db.patients
    medecins_coll = db.medecins

    try:
        # 1. Récupérer les consultations les plus récentes
        raw_consultations = list(
            consultations_coll.find()
            .sort("date", -1)
            .limit(limit)
        )

        formatted_consultations = []

        for consult in raw_consultations:
            # 2. Récupérer patient
            patient = patients_coll.find_one({"_id": consult.get("id_patient")})
            if patient:
                nom_patient = f"{patient.get('prenom', '')} {patient.get('nom', '')}".strip()
            else:
                nom_patient = "Patient Inconnu"

            # 3. Récupérer médecin
            medecin = medecins_coll.find_one({"_id": consult.get("id_medecin")})
            if medecin:
                nom_medecin = f"Dr. {medecin.get('prenom', '')} {medecin.get('nom', '')}".strip()
            else:
                nom_medecin = "Médecin Inconnu"

            # 4. Formatage date
            date_str = consult.get("date", "Date Inconnue")
            try:
                date_obj = datetime.strptime(date_str, "%Y-%m-%d")
                display_date = date_obj.strftime("%d/%m/%Y")
            except (ValueError, TypeError):
                display_date = date_str

            formatted_consultations.append({
                "id": str(consult["_id"]),
                "nom_patient": nom_patient,
                "nom_medecin": nom_medecin,
                "date": display_date,
                "diagnostic": consult.get("diagnostic", "N/A"),
                "prescriptions": consult.get("prescriptions", []),
                "notes": consult.get("notes", "")
            })

        return formatted_consultations

    except Exception as e:
        print(f"Erreur lors de la récupération des consultations : {e}")
        return []



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