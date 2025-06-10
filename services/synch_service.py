from services.mongo_service import (
    get_all_patients,
    get_all_medecins,
    get_all_consultations,
    get_all_users
)
from services.neo4j_service import (
    create_patient_node,
    create_medecin_node,
    create_utilisateur_node,
    delete_patient_node,
    delete_medecin_node,
    delete_utilisateur_node,
    driver
)

# === PATIENTS ===

def sync_patients():
    patients = get_all_patients()
    for patient in patients:
        patient_data = {
            "id": str(patient["_id"]),
            "nom": patient.get("nom", ""),
            "prenom": patient.get("prenom", ""),
            "age": patient.get("age", 0),
            "sexe": patient.get("sexe", ""),
            "date_naissance": patient.get("date_naissance", ""),
            "adresse": patient.get("adresse", ""),
            "telephone": patient.get("telephone", ""),
            "email": patient.get("email", ""),
            "cin": patient.get("cin", "")
        }
        delete_patient_node(patient_data["id"])
        create_patient_node(patient_data)

# === MEDECINS ===

def sync_medecins():
    medecins = get_all_medecins()
    for medecin in medecins:
        medecin_data = {
            "id": str(medecin["_id"]),
            "nom": medecin.get("nom", ""),
            "specialite": medecin.get("specialite", ""),
            "adresse": medecin.get("adresse", ""),
            "num_tel": medecin.get("num_tel", ""),
            "email": medecin.get("email", ""),
            "disponibilite": medecin.get("disponibilite", []),
            "experiences": medecin.get("experiences", "")
        }
        delete_medecin_node(medecin_data["id"])
        create_medecin_node(medecin_data)

# === CONSULTATIONS ===

def sync_consultations_from_mongo():
    consultations = get_all_consultations()
    with driver.session() as session:
        for consult in consultations:
            id_patient = str(consult["id_patient"])
            id_medecin = str(consult["id_medecin"])

            properties = {
                "id_patient": id_patient,
                "id_medecin": id_medecin,
                "date": consult.get("date", ""),
                "diagnostic": consult.get("diagnostic", ""),
                "traitement": consult.get("traitement", ""),
                "ordonnance": ", ".join(consult.get("prescriptions", [])),  
                "notes": consult.get("notes", "")
            }

            query = """
            MATCH (p:Patient {id: $id_patient})
            MATCH (m:Medecin {id: $id_medecin})
            MERGE (p)-[r:A_CONSULTE {
                date: $date,
                diagnostic: $diagnostic,
                traitement: $traitement,
                ordonnance: $ordonnance,
                notes: $notes
            }]->(m)
            """

            session.run(query, **properties)

    print("✅ Consultations synchronisées vers Neo4j.")

# === UTILISATEURS ===

def sync_utilisateurs():
    utilisateurs = get_all_users()
    with driver.session() as session:
        for user in utilisateurs:
            utilisateur_data = {
                "id": str(user["_id"]),
                "id_fonctionnel": str(user.get("id_fonctionnel", "")),
                "email": user.get("email", ""),
                "mot_de_passe": user.get("mot_de_passe", ""),
                "role": user.get("role", ""),
                "date_creation": str(user.get("date_creation", "")),
                "nom": user.get("nom", "")
            }

            # Supprimer ancien noeud + relation
            delete_utilisateur_node(utilisateur_data["id"])
            create_utilisateur_node(utilisateur_data)

            # Créer relation vers Patient ou Médecin
            relation_query = ""
            if utilisateur_data["role"] == "patient":
                relation_query = """
                MATCH (u:Utilisateur {id: $id})
                MATCH (p:Patient {id: $id_fonctionnel})
                MERGE (u)-[:EST]->(p)
                """
            elif utilisateur_data["role"] == "medecin":
                relation_query = """
                MATCH (u:Utilisateur {id: $id})
                MATCH (m:Medecin {id: $id_fonctionnel})
                MERGE (u)-[:EST]->(m)
                """

            if relation_query:
                session.run(relation_query, id=utilisateur_data["id"], id_fonctionnel=utilisateur_data["id_fonctionnel"])

    print("✅ Utilisateurs et relations fonctionnelles synchronisés vers Neo4j.")

# === GLOBAL ===

def sync_all():
    print("🔄 Synchronisation des patients...")
    sync_patients()
    print("🔄 Synchronisation des médecins...")
    sync_medecins()
    print("🔄 Synchronisation des consultations...")
    sync_consultations_from_mongo()
    print("🔄 Synchronisation des utilisateurs...")
    sync_utilisateurs()
    print("✅ Synchronisation terminée.")
