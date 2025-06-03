from services.mongo_service import (
    insert_patient, get_all_patients, get_patient_by_id,
    update_patient, delete_patient
)
from services.neo4j_service import (
    create_patient_node, delete_patient_node, update_patient_node
)

def create_patient(patient_data):
    result = insert_patient(patient_data)
    patient_id = str(result.inserted_id)
    try:
        create_patient_node(patient_id, patient_data)
    except Exception as e:
        print(f"[Neo4j] Erreur lors de la création du noeud patient : {e}")
    return patient_id

def get_patients():
    return get_all_patients()

def get_patient(patient_id):
    return get_patient_by_id(patient_id)

def modify_patient(patient_id, updated_data):
    result = update_patient(patient_id, updated_data)
    try:
        update_patient_node(patient_id, updated_data)
    except Exception as e:
        print(f"[Neo4j] Erreur lors de la mise à jour du noeud patient : {e}")
    return result

def remove_patient(patient_id):
    result = delete_patient(patient_id)
    try:
        delete_patient_node(patient_id)
    except Exception as e:
        print(f"[Neo4j] Erreur lors de la suppression du noeud patient : {e}")
    return result
