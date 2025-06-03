from services.mongo_service import (
    insert_medecin, get_all_medecins, get_medecin_by_id,
    update_medecin, delete_medecin
)
from services.neo4j_service import (
    create_medecin_node, delete_medecin_node, update_medecin_node
)

def create_medecin(medecin_data):
    result = insert_medecin(medecin_data)
    medecin_id = str(result.inserted_id)
    try:
        create_medecin_node(medecin_id, medecin_data)
    except Exception as e:
        print(f"[Neo4j] Erreur lors de la création du noeud médecin : {e}")
    return medecin_id

def get_medecins():
    return get_all_medecins()

def get_medecin(medecin_id):
    return get_medecin_by_id(medecin_id)

def modify_medecin(medecin_id, updated_data):
    result = update_medecin(medecin_id, updated_data)
    try:
        update_medecin_node(medecin_id, updated_data)
    except Exception as e:
        print(f"[Neo4j] Erreur lors de la mise à jour du noeud médecin : {e}")
    return result

def remove_medecin(medecin_id):
    result = delete_medecin(medecin_id)
    try:
        delete_medecin_node(medecin_id)
    except Exception as e:
        print(f"[Neo4j] Erreur lors de la suppression du noeud médecin : {e}")
    return result
