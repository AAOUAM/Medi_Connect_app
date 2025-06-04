from services.mongo_service import (
    insert_medecin, get_medecin_by_id,
    get_all_medecins, update_medecin,
    delete_medecin
)

from services.neo4j_service import (
    create_medecin_node, update_medecin_node,
    delete_medecin_node
)

def create_medecin(data):
    result = insert_medecin(data)
    medecin_id = str(result.inserted_id)

    neo4j_data = {
        "id": medecin_id,
        "nom": data["nom"],
        "specialite": data["specialite"],
        "adresse": data["adresse"],
        "num_tel": data["num_tel"],
        "email": data["email"],
        "disponibilite": data["disponibilite"],
        "experiences": data["experiences"]
    }
    create_medecin_node(neo4j_data)
    return medecin_id

def retrieve_medecin(medecin_id):
    return get_medecin_by_id(medecin_id)

def retrieve_all_medecins():
    return get_all_medecins()

def update_medecin_record(medecin_id, updated_data):
    medecin = get_medecin_by_id(medecin_id)
    if not medecin:
        raise ValueError("Médecin introuvable")

    update_medecin(medecin_id, updated_data)

    updated_medecin = {**medecin, **updated_data}
    neo4j_data = {
        "id": medecin_id,
        "nom": updated_medecin["nom"],
        "specialite": updated_medecin["specialite"],
        "adresse": updated_medecin["adresse"],
        "num_tel": updated_medecin["num_tel"],
        "email": updated_medecin["email"],
        "disponibilite": updated_medecin["disponibilite"],
        "experiences": updated_medecin["experiences"]
    }
    update_medecin_node(neo4j_data)

def delete_medecin_record(medecin_id):
    delete_medecin(medecin_id)
    delete_medecin_node(medecin_id)
