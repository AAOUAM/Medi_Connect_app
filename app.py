from flask import Flask, render_template, json , flash, redirect, url_for , request
import services.mongo_service as mongo_service 
import models.patient as Patient


app = Flask(__name__)


@app.route('/') 
@app.route('/admin/dashboard')
def dashboard_admin():
    nb_patients, nb_medecins, nb_total_consultations, nb_utilisateurs = 0, 0, 0, 0
    recent_consultations = []
    monthly_stats = {"labels": [], "data": []}

    nb_patients = mongo_service.count_patients()
    nb_medecins = mongo_service.count_medecins()
    nb_total_consultations = mongo_service.count_consultations() # Renommé pour clarté
    nb_utilisateurs = mongo_service.count_users()

    # Utiliser la fonction de service qui fait déjà les lookups et le formatage
    recent_consultations = mongo_service.get_recent_consultations_with_details(limit=5)
        
    # Récupérer les données pour le graphique d'évolution mensuelle
    monthly_stats = mongo_service.get_monthly_consultation_stats()


    return render_template("dashboard_admin.html",
                           nb_patients=nb_patients,
                           nb_medecins=nb_medecins,
                           # Passer le nombre total pour la carte stat, et la liste pour le tableau
                           nb_consultations=nb_total_consultations, 
                           nb_utilisateurs=nb_utilisateurs,
                           consultations=recent_consultations, # C'est la liste enrichie et limitée
                           # Sérialiser en JSON pour le JavaScript
                           monthly_consultation_labels=json.dumps(monthly_stats.get('labels', [])),
                           monthly_consultation_data=json.dumps(monthly_stats.get('data', []))
                           )






# --- Routes  de GESTION ---

@app.route('/admin/patients/manage') 
def manage_patients():
    try:
        all_patients_list = mongo_service.get_all_patients() # Fonction de votre service
    except Exception as e:
        print(f"Erreur lors de la récupération des patients: {e}")
        flash("Erreur lors du chargement de la liste des patients.", "danger")
        all_patients_list = []
    return render_template('manage_patients.html', patients=all_patients_list)


@app.route('/admin/medecins/manage')
def manage_medecins():
    all_medecins_list = []
    all_medecins_list = mongo_service.get_all_medecins() 
    return render_template('manage_medecins.html', medecins=all_medecins_list)

@app.route('/admin/consultations/manage')
def manage_consultations():
    return "Page de gestion des consultations (à implémenter)"

@app.route('/admin/users/manage') # J'utilise /manage pour la page de liste
def manage_users():
    return "Page de gestion des utilisateurs (à implémenter)"

@app.route('/logout')
def logout():
    # À implémenter: session.clear(), flash message, redirect to login
    return "Déconnexion (à implémenter)"





# --- Routes  de PATIENTS ---

@app.route('/add_patient', methods=['GET', 'POST'])
def add_patient():
    if request.method == 'POST':
        form_data = {
            'nom': request.form.get('nom', '').strip(),
            'prenom': request.form.get('prenom', '').strip(),
            'age': int(request.form.get('age', 0)),
            'adresse': request.form.get('adresse', '').strip(),
            'telephone': request.form.get('telephone', '').strip(),
            'email': request.form.get('email', '').strip(),
        }

        # Validation simple
        if not form_data['nom'] or not form_data['prenom'] or form_data['age'] <= 0:
            error = "Veuillez remplir tous les champs obligatoires correctement."
            return render_template('patient_form.html', patient=form_data, error=error)

        Patient.create_patient(form_data)
        return redirect(url_for('manage_patients'))

    # GET request : afficher le formulaire vide
    return render_template('patient_form.html', patient=None)


@app.route('/edit_patient/<string:patient_id_str>', methods=['GET', 'POST'])
def edit_patient(patient_id_str):
    if request.method == 'POST':
        updated_data = {
            'nom': request.form.get('nom', '').strip(),
            'prenom': request.form.get('prenom', '').strip(),
            'age': int(request.form.get('age', 0)),
            'adresse': request.form.get('adresse', '').strip(),
            'telephone': request.form.get('telephone', '').strip(),
            'email': request.form.get('email', '').strip(),
        }

        Patient.modify_patient(patient_id_str, updated_data)
        return redirect(url_for('manage_patients'))

    patient = Patient.get_patient(patient_id_str)
    return render_template('patient_form.html', patient=patient)



# @app.route('/delete_patient/<string:patient_id_str>', methods=['POST'])
# def delete_patient_route(patient_id_str):
#     Patient.remove_patient(patient_id_str)
#     return redirect(url_for('/admin/patients/manage'))


@app.route('/delete_patient/<string:patient_id_str>', methods=['POST'])
def delete_patient(patient_id_str):
    mongo_service.delete_patient(patient_id_str)
    return redirect(url_for('manage_patients'))


@app.route('/admin/patients/<patient_id_str>')
def view_patient(patient_id_str):
    try:
        patient = mongo_service.get_patient_by_id(patient_id_str)  # Cette fonction doit être définie dans mongo_service
        if not patient:
            flash("Patient non trouvé.", "warning")
            return redirect(url_for('manage_patients'))
    except Exception as e:
        print(f"Erreur lors de la récupération du patient: {e}")
        flash("Erreur serveur.", "danger")
        return redirect(url_for('manage_patients'))

    return render_template('view_patient.html', patient=patient)



# --- Routes pour Actions CRUD (Placeholders) ---






@app.route('/admin/medecins/add', methods=['GET', 'POST'])
def add_medecin():
    return "Page pour ajouter un médecin (à implémenter)"

@app.route('/admin/consultations/add', methods=['GET', 'POST'])
def add_consultation():
    # Pour GET:
    # patients = mongo_service.get_all_patients()
    # medecins = mongo_service.get_all_medecins()
    # return render_template('ajouter_consultation.html', patients=patients, medecins=medecins)
    return "Page pour ajouter une consultation (à implémenter)"

# Routes pour les actions sur les consultations (dans le tableau du dashboard)
# Elles nécessitent un <consult_id>
@app.route('/view_consultation/<consult_id_str>')
def view_consultation(consult_id_str):
    # consult = mongo_service.get_consultation_by_id(consult_id_str) # ou une version avec détails
    # if consult:
    #     patient = mongo_service.get_patient_by_id(str(consult['id_patient']))
    #     medecin = mongo_service.get_medecin_by_id(str(consult['id_medecin']))
    #     return render_template('view_consultation.html', consultation=consult, patient=patient, medecin=medecin)
    # flash('Consultation non trouvée.', 'danger')
    # return redirect(url_for('dashboard_admin'))
    return f"Voir consultation {consult_id_str} (à implémenter)"

@app.route('/edit_consultation/<consult_id_str>', methods=['GET', 'POST'])
def edit_consultation(consult_id_str):
    # if request.method == 'POST':
    #    # ...
    # else: (GET)
    #    consult = mongo_service.get_consultation_by_id(consult_id_str)
    #    # ... charger le formulaire avec les données de consult
    return f"Modifier consultation {consult_id_str} (à implémenter)"

@app.route('/delete_consultation/<consult_id_str>', methods=['POST']) # Sécuriser avec POST
def delete_consultation(consult_id_str):
    # mongo_service.delete_consultation(consult_id_str) # Vous aurez besoin de cette fonction
    # flash('Consultation supprimée.', 'success')
    # return redirect(url_for('dashboard_admin'))
    return f"Supprimer consultation {consult_id_str} (nécessite confirmation et méthode POST, à implémenter)"


if __name__ == "__main__":
    app.run(debug=True, port=1000)