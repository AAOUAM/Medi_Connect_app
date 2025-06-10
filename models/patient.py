from services.mongo_service import (
    insert_patient, get_patient_by_id,
    get_all_patients, update_patient,
    delete_patient
)

from services.neo4j_service import (
    create_patient_node, update_patient_node,
    delete_patient_node
)

def create_patient(data):
    result = insert_patient(data)
    patient_id = str(result.inserted_id)

    neo4j_data = {
        "id": patient_id,
        "nom": data["nom"],
        "prenom": data["prenom"],
        "age": data["age"],
        "telephone": data["telephone"],
        "email": data["email"],
        "adresse": data["adresse"],
        "cin": data["cin"]
    }
    create_patient_node(neo4j_data)
    return patient_id

def retrieve_patient(patient_id):
    return get_patient_by_id(patient_id)

def retrieve_all_patients():
    return get_all_patients()

def update_patient_record(patient_id, updated_data):
    patient = get_patient_by_id(patient_id)
    if not patient:
        raise ValueError("Patient introuvable")

    update_patient(patient_id, updated_data)

    # fusion des données mises à jour avec les anciennes
    updated_patient = {**patient, **updated_data}
    neo4j_data = {
        "id": patient_id,
        "nom": updated_patient["nom"],
        "prenom": updated_patient["prenom"],
        "age": updated_patient["age"],
        "telephone": updated_patient["telephone"],
        "email": updated_patient["email"],
        "adresse": updated_patient["adresse"],
        "cin": update_patient["cin"],
    }
    update_patient_node(neo4j_data)

def delete_patient_record(patient_id):
    delete_patient(patient_id)
    delete_patient_node(patient_id)
