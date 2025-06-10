from neo4j import GraphDatabase
from config import NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD

driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))

# === PATIENTS (CRUD) ===

def create_patient_node(patient_data):
    with driver.session() as session:
        session.run("""
            CREATE (p:Patient {
                id: $id, nom: $nom, prenom: $prenom, age: $age,
                adresse: $adresse, telephone: $telephone,
                email: $email, cin: $cin
            })
        """, **patient_data)

def get_all_patients():
    with driver.session() as session:
        result = session.run("MATCH (p:Patient) RETURN p")
        return [record["p"] for record in result]

def get_patient_by_id(id_value):
    with driver.session() as session:
        result = session.run("MATCH (p:Patient {id: $id}) RETURN p", id=id_value)
        return result.single()["p"] if result.single() else None

def update_patient_node(id_value, updated_data):
    with driver.session() as session:
        session.run("""
            MATCH (p:Patient {id: $id})
            SET p.nom = $nom, p.prenom = $prenom, p.age = $age,
                p.adresse = $adresse, p.telephone = $telephone,
                p.email = $email, p.cin = $cin
        """, id=id_value, **updated_data)

def delete_patient_node(id_value):
    with driver.session() as session:
        session.run("MATCH (p:Patient {id: $id}) DETACH DELETE p", id=id_value)


# === MEDECINS (CRUD) ===

def create_medecin_node(medecin_data):
    with driver.session() as session:
        session.run("""
            CREATE (m:Medecin {
                id: $id, nom: $nom, specialite: $specialite,
                adresse: $adresse, num_tel: $num_tel,
                email: $email, disponibilite: $disponibilite,
                experiences: $experiences
            })
        """, **medecin_data)

def get_all_medecins():
    with driver.session() as session:
        result = session.run("MATCH (m:Medecin) RETURN m")
        return [record["m"] for record in result]

def get_medecin_by_id(id_value):
    with driver.session() as session:
        result = session.run("MATCH (m:Medecin {id: $id}) RETURN m", id=id_value)
        return result.single()["m"] if result.single() else None

def update_medecin_node(id_value, updated_data):
    with driver.session() as session:
        session.run("""
            MATCH (m:Medecin {id: $id})
            SET m.nom = $nom, m.specialite = $specialite,
                m.adresse = $adresse, m.num_tel = $num_tel,
                m.email = $email, m.disponibilite = $disponibilite,
                m.experiences = $experiences
        """, id=id_value, **updated_data)

def delete_medecin_node(id_value):
    with driver.session() as session:
        session.run("MATCH (m:Medecin {id: $id}) DETACH DELETE m", id=id_value)


# === UTILISATEURS (CRUD) ===

def create_utilisateur_node(utilisateur_data):
    with driver.session() as session:
        session.run("""
            CREATE (u:Utilisateur {
                id: $id, id_fonctionnel: $id_fonctionnel,
                email: $email, mot_de_passe: $mot_de_passe,
                role: $role, date_creation: $date_creation,
                nom: $nom
            })
        """, **utilisateur_data)

def get_all_utilisateurs():
    with driver.session() as session:
        result = session.run("MATCH (u:Utilisateur) RETURN u")
        return [record["u"] for record in result]

def get_utilisateur_by_id(id_value):
    with driver.session() as session:
        result = session.run("MATCH (u:Utilisateur {id: $id}) RETURN u", id=id_value)
        return result.single()["u"] if result.single() else None

def update_utilisateur_node(id_value, updated_data):
    with driver.session() as session:
        session.run("""
            MATCH (u:Utilisateur {id: $id})
            SET u.id_fonctionnel = $id_fonctionnel,
                u.email = $email, u.mot_de_passe = $mot_de_passe,
                u.role = $role, u.date_creation = $date_creation,
                u.nom = $nom
        """, id=id_value, **updated_data)

def delete_utilisateur_node(id_value):
    with driver.session() as session:
        session.run("MATCH (u:Utilisateur {id: $id}) DETACH DELETE u", id=id_value)
