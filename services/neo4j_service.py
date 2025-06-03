from neo4j import GraphDatabase
from config import NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD

driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))

# === PATIENTS ===

def create_patient_node(patient_data):
    """Créer un noeud Patient"""
    with driver.session() as session:
        session.run("""
            CREATE (p:Patient {id: $id, nom: $nom, prenom: $prenom, age: $age})
        """, **patient_data)

def get_all_patients():
    """Récupérer tous les noeuds Patient"""
    with driver.session() as session:
        result = session.run("MATCH (p:Patient) RETURN p")
        return [record["p"] for record in result]

def get_patient_by_id(id_value):
    """Récupérer un Patient par son id"""
    with driver.session() as session:
        result = session.run("""
            MATCH (p:Patient {id: $id})
            RETURN p
        """, id=id_value)
        return result.single()["p"] if result.single() else None

def update_patient_node(id_value, updated_data):
    """Mettre à jour un Patient"""
    with driver.session() as session:
        session.run("""
            MATCH (p:Patient {id: $id})
            SET p.nom = $nom, p.prenom = $prenom, p.age = $age
        """, id=id_value, **updated_data)

def delete_patient_node(id_value):
    """Supprimer un Patient"""
    with driver.session() as session:
        session.run("MATCH (p:Patient {id: $id}) DETACH DELETE p", id=id_value)

# === MEDECINS ===

def create_medecin_node(medecin_data):
    """Créer un noeud Médecin"""
    with driver.session() as session:
        session.run("""
            CREATE (m:Medecin {id: $id, nom: $nom, specialite: $specialite})
        """, **medecin_data)

def get_all_medecins():
    """Récupérer tous les noeuds Médecin"""
    with driver.session() as session:
        result = session.run("MATCH (m:Medecin) RETURN m")
        return [record["m"] for record in result]

def get_medecin_by_id(id_value):
    """Récupérer un Médecin par son id"""
    with driver.session() as session:
        result = session.run("""
            MATCH (m:Medecin {id: $id})
            RETURN m
        """, id=id_value)
        return result.single()["m"] if result.single() else None

def update_medecin_node(id_value, updated_data):
    """Mettre à jour un Médecin"""
    with driver.session() as session:
        session.run("""
            MATCH (m:Medecin {id: $id})
            SET m.nom = $nom, m.specialite = $specialite
        """, id=id_value, **updated_data)

def delete_medecin_node(id_value):
    """Supprimer un Médecin"""
    with driver.session() as session:
        session.run("MATCH (m:Medecin {id: $id}) DETACH DELETE m", id=id_value)


