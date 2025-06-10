from services.mongo_service import (
    get_consultation_by_id,
    get_all_consultations,
    get_consultations_by_medecin,
    get_consultations_by_patient_id  # À utiliser si défini
)

def retrieve_consultation(consultation_id):
    return get_consultation_by_id(consultation_id)

def retrieve_all_consultations():
    return get_all_consultations()

def retrieve_consultations_by_medecin(medecin_id):
    return get_consultations_by_medecin(medecin_id)

def retrieve_consultations_by_patient(patient_id):
    return get_consultations_by_patient_id (patient_id)