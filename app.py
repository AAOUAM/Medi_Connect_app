from flask import Flask, render_template, json , flash, redirect, url_for , request
import services.mongo_service as mongo_service 
from models import utilisateur  # à créer si ce n'est pas fait


from models import patient
from models import medecin  


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
  consultations = mongo_service.get_all_consultations()

  for c in consultations:
    # Récupère les noms du patient et du médecin
    patient = mongo_service.get_patient_by_id(c['id_patient'])
    medecin = mongo_service.get_medecin_by_id(c['id_medecin'])

    # Ajoute les noms dans chaque consultation
    c['nom_patient'] = f"{patient.get('nom', 'N/A')} {patient.get('prenom', '')}" if patient else "Inconnu"
    c['nom_medecin'] = f"{medecin.get('nom', 'N/A')} {medecin.get('prenom', '')}" if medecin else "Inconnu"

  return render_template('manage_consultations.html', consultations=consultations)

@app.route('/admin/users/manage') # J'utilise /manage pour la page de liste
def manage_users():
    all_users_list = mongo_service.get_all_users()
    return render_template('manage_users.html', utilisateurs=all_users_list)

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
            'cin': request.form.get('cin', '').strip(),
        }

        # Validation simple
        if not form_data['nom'] or not form_data['prenom'] or form_data['age'] <= 0:
            error = "Veuillez remplir tous les champs obligatoires correctement."
            return render_template('patient_form.html', patient=form_data, error=error)

        patient.create_patient(form_data)
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
            'cin': request.form.get('cin', '').strip(),
        }

        patient.modify_patient(patient_id_str, updated_data)
        return redirect(url_for('manage_patients'))

    patient = patient.get_patient(patient_id_str)
    return render_template('patient_form.html', patient=patient)



# @app.route('/delete_patient/<string:patient_id_str>', methods=['POST'])
# def delete_patient_route(patient_id_str):
#     Patient.remove_patient(patient_id_str)
#     return redirect(url_for('/admin/patients/manage'))


@app.route('/delete_patient/<string:patient_id_str>', methods=['POST'])
def delete_patient(patient_id_str):
    mongo_service.delete_patient(patient_id_str)
    return redirect(url_for('manage_patients'))









# --- Routes pour MEDECINS ---

@app.route('/admin/medecins/add', methods=['GET', 'POST'])
def add_medecin():
    if request.method == 'POST':
        form_data = {
            'nom': request.form['nom'],
            'specialite': request.form['specialite'],
            'adresse': request.form['adresse'],
            'num_tel': request.form.get('num_tel', '').strip(),
            'email': request.form['email'],
            'disponibilite': request.form.getlist('disponibilite'),
            'experiences': request.form['experiences'],
        }
        medecin.create_medecin(form_data)
        return redirect(url_for('manage_medecins'))

    return render_template('medecin_form.html', medecin=None)

@app.route('/admin/medecins/edit/<string:medecin_id>', methods=['GET', 'POST'])
def edit_medecin(medecin_id):
    medecin_data = medecin.get_medecin(medecin_id)
    if not medecin_data:
        return "Médecin non trouvé", 404

    if request.method == 'POST':
        updated_data = {
            'nom': request.form['nom'],
            'specialite': request.form['specialite'],
            'adresse': request.form['adresse'],
            'num_tel': request.form.get('num_tel', '').strip(),
            'email': request.form['email'],
            'disponibilite': request.form.getlist('disponibilite'),
            'experiences': request.form['experiences'],
        }
        medecin.modify_medecin(medecin_id, updated_data)
        return redirect(url_for('manage_medecins'))

    return render_template('medecin_form.html', medecin=medecin_data)

@app.route('/admin/medecins/delete/<string:medecin_id>', methods=['POST'])
def delete_medecin(medecin_id):
    medecin.remove_medecin(medecin_id)
    return redirect(url_for('manage_medecins'))







# --- Routes pour CONSUTLTATIONS ---

@app.route('/admin/consultations/add', methods=['GET', 'POST'])
def add_consultation():
    if request.method == 'POST':
        form_data = {
            'id_patient': request.form['id_patient'],
            'id_medecin': request.form['id_medecin'],
            'date': request.form['date'],
            'diagnostic': request.form['diagnostic'],
            'prescriptions': request.form['prescriptions'].split(','),  # comma-separated
            'notes': request.form['notes']
        }
        mongo_service.insert_consultation(form_data)
        return redirect(url_for('manage_consultations'))
    
    return render_template('consultation_form.html', consultation=None)




# --- Routes  de PATIENTS ---

@app.route('/admin/users/add', methods=['GET', 'POST'])
def add_user():
    if request.method == 'POST':
        form_data = {
            'nom': request.form.get('nom', '').strip(),
            'email': request.form.get('email', '').strip(),
            'role': request.form.get('role', '').strip(),
            'mot_de_passe': request.form.get('mot_de_passe', '').strip(),
        }

        # Validation basique
        if not form_data['nom'] or not form_data['email'] or not form_data['role']:
            error = "Tous les champs obligatoires doivent être remplis."
            return render_template('user_form.html', utilisateur=form_data, error=error)

        utilisateur.create_utilisateur(form_data)
        return redirect(url_for('manage_users'))

    return render_template('user_form.html', utilisateur=None)


@app.route('/admin/users/edit/<string:utilisateur_id>', methods=['GET', 'POST'])
def edit_user(utilisateur_id):
    user_data = utilisateur.get_utilisateur_by_id(utilisateur_id)
    if not user_data:
        return "Utilisateur non trouvé", 404

    if request.method == 'POST':
        updated_data = {
            'nom': request.form.get('nom', '').strip(),
            'email': request.form.get('email', '').strip(),
            'role': request.form.get('role', '').strip(),
            'mot_de_passe': request.form.get('mot_de_passe', '').strip(),  # ou gérer conditionnellement
        }

        utilisateur.modify_utilisateur(utilisateur_id, updated_data)
        return redirect(url_for('manage_users'))

    return render_template('user_form.html', utilisateur=user_data)


@app.route('/admin/users/delete/<string:utilisateur_id>', methods=['POST'])
def delete_user(utilisateur_id):
    utilisateur.delete_utilisateur_record(utilisateur_id)
    return redirect(url_for('manage_users'))




if __name__ == "__main__":
    app.run(debug=True, port=1000)