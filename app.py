from flask import Flask, render_template, json , flash, redirect, url_for , request ,  session, flash 
import services.mongo_service as mongo_service 
from models import utilisateur 
from services.synch_service import sync_all
from services.auth_service import AuthService, login_required, admin_required, medecin_required, patient_required
from bson.objectid import ObjectId 
from datetime import datetime

from models import patient
from models import medecin  
from models import utilisateur



app = Flask(__name__)
app.secret_key = ' '


# ==================== ROUTES D'AUTHENTIFICATION ====================

@app.route('/')
def index():
    if 'user_id' in session:
        user_role = session.get('user_role')
        if user_role == 'admin':
            return redirect(url_for('dashboard_admin'))
        elif user_role == 'medecin':
            return redirect(url_for('medecin_dashboard'))
        elif user_role == 'patient':
            return redirect(url_for('patient_dashboard'))
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    # Étape 1: Si l'utilisateur est déjà connecté, rediriger immédiatement
    if 'user_id' in session and 'user_role' in session:
        user_role = session['user_role']    
        if user_role == 'admin':
            return redirect(url_for('dashboard_admin'))
        elif user_role == 'medecin':
            # Assurez-vous que le nom de la route est correct
            return redirect(url_for('medecin_dashboard'))
        elif user_role == 'patient':
            return redirect(url_for('patient_dashboard'))

    # Étape 2: Si c'est une soumission de formulaire (POST)
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')

        if not email or not password:
            flash('Veuillez remplir tous les champs', 'error')
            return render_template('login.html')

        result = AuthService.authenticate_user(email, password)

        if result['success']:
            user = result['user']
            session.permanent = True
            session['user_id'] = str(user['id'])
            session['user_email'] = user['email']
            session['user_role'] = user['role']
            session['user_nom'] = user.get('nom', '')
            session['id_fonctionnel'] = str(user.get('id_fonctionnel', ''))

            flash(f"Bienvenue {session['user_nom']}!", 'success')
            
            # Rediriger après une connexion réussie
            if user['role'] == 'admin':
                return redirect(url_for('dashboard_admin'))
            elif user['role'] == 'medecin':
                return redirect(url_for('medecin_dashboard'))
            elif user['role'] == 'patient':
                return redirect(url_for('patient_dashboard'))
        else:
            flash(result['message'], 'error')

    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    user_name = session.get('user_prenom', '') or session.get('user_email', 'Utilisateur')
    session.clear()
    flash(f'Au revoir {user_name}! Vous avez été déconnecté.', 'info')
    return redirect(url_for('login'))  





# ==================== ROUTES D'ADMINISTRATION ====================

@app.route('/admin/')
@app.route('/admin/dashboard')
def dashboard_admin():
    nb_patients, nb_medecins, nb_total_consultations, nb_utilisateurs = 0, 0, 0, 0
    recent_consultations = []
    monthly_stats = {"labels": [], "data": []}

    nb_patients = mongo_service.count_patients()
    nb_medecins = mongo_service.count_medecins()
    nb_total_consultations = mongo_service.count_consultations() 
    nb_utilisateurs = mongo_service.count_users()

    recent_consultations = mongo_service.get_recent_consultations_with_details(limit=5)
        
    monthly_stats = mongo_service.get_monthly_consultation_stats()

    admin_user = session.get('user_nom')

    return render_template("dashboard_admin.html",
                           admin_user_nom=admin_user,
                           nb_patients=nb_patients,
                           nb_medecins=nb_medecins,
                           # Passer le nombre total pour la carte stat, et la liste pour le tableau
                           nb_consultations=nb_total_consultations, 
                           nb_utilisateurs=nb_utilisateurs,
                           consultations=recent_consultations, # C'est la liste enrichie et limitée
                           
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

@app.route('/admin/users/manage')
def manage_users():
    all_users_list = mongo_service.get_all_users()
    return render_template('manage_users.html', utilisateurs=all_users_list)



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
        sync_all()
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
        sync_all()
        return redirect(url_for('manage_patients'))

    patient = patient.get_patient(patient_id_str)
    return render_template('patient_form.html', patient=patient)


@app.route('/delete_patient/<string:patient_id_str>', methods=['POST'])
def delete_patient(patient_id_str):
    mongo_service.delete_patient(patient_id_str)
    sync_all()
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
        sync_all()
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
        sync_all()
        return redirect(url_for('manage_medecins'))

    return render_template('medecin_form.html', medecin=medecin_data)

@app.route('/admin/medecins/delete/<string:medecin_id>', methods=['POST'])
def delete_medecin(medecin_id):
    medecin.remove_medecin(medecin_id)
    sync_all()
    return redirect(url_for('manage_medecins'))




# --- Routes  de UTILISATEURS ---
@app.route('/admin/users/add', methods=['GET', 'POST'])
def add_user():
    if request.method == 'POST':
        form_data = {
            'nom': request.form.get('nom', '').strip(),
            'email': request.form.get('email', '').strip(),
            'role': request.form.get('role', '').strip(),
            'password': request.form.get('password', '').strip(),
        }

        # Validation basique
        if not form_data['nom'] or not form_data['email'] or not form_data['role']:
            error = "Tous les champs obligatoires doivent être remplis."
            return render_template('user_form.html', utilisateur=form_data, error=error)

        AuthService.create_user(form_data["email"] , form_data["password"] , form_data["role"] , form_data["nom"])
        sync_all()
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
        sync_all()
        return redirect(url_for('manage_users'))

    return render_template('user_form.html', utilisateur=user_data)


@app.route('/admin/users/delete/<string:utilisateur_id>', methods=['POST'])
def delete_user(utilisateur_id):
    utilisateur.delete_utilisateur_record(utilisateur_id)
    sync_all()
    return redirect(url_for('manage_users'))





# ==================== ROUTES DE MEDECIN ====================
@app.route("/medecin/dashboard")
def medecin_dashboard():
  user_id = session.get('user_id')

  utilisateur = mongo_service.get_utilisateur_by_id(user_id)

  user_id_fonctionnel = utilisateur.get('id_fonctionnel')

  if not user_id_fonctionnel:
    flash("Votre compte n'est pas associé à un profil médecin valide.", "error")
    return redirect(url_for('logout')) # On déconnecte pour être sûr

  # Étape 3 : récupérer les infos médecin
  medecin_info = mongo_service.get_medecin_by_id(user_id_fonctionnel)
  # Étape 4 : charger les consultations
  consultations_fictives = mongo_service.get_consultations_by_medecin(user_id_fonctionnel)

  return render_template(
    'medecin_dashboard.html',
    medecin=medecin_info,
    consultations=consultations_fictives
  )


@app.route('/medecin/consultation/add', methods=['GET', 'POST'])
def add_consultation():
    if request.method == 'GET':
        return render_template('consultation_form.html', consultation=None)

    if request.method == 'POST':

        if session.get('id_fonctionnel'):
            medecin_id_fonctionnel = ObjectId(session['id_fonctionnel'])
        else:
            # Gérer l'erreur proprement
            flash("Identifiant fonctionnel du médecin introuvable.", 'error')
            return redirect(url_for('login'))

        patient_full_name = request.form.get('patient_full_name', '').strip()

        patient = mongo_service.get_patient_by_nom(patient_full_name)

        # 3. GESTION D'ERREUR CRITIQUE : que faire si le patient n'est pas trouvé ?
        if not patient:
            flash(f"Patient '{patient_full_name}' non trouvé. Veuillez vérifier l'orthographe ou créer le patient.", "error")
            # On renvoie le formulaire avec les données déjà saisies pour ne pas tout perdre
            return render_template('consultation_form.html', consultation=request.form, error=True)

        # Si le patient est trouvé, on récupère son ID
        patient_id = patient['_id']

        # 4. Récupérer les autres données du formulaire
        date_str = request.form.get('date')
        diagnostic = request.form.get('diagnostic', '').strip()
        notes = request.form.get('notes', '').strip()
        prescriptions_list = request.form.getlist('prescriptions[]')
        prescriptions = [p.strip() for p in prescriptions_list if p.strip()]

        consultation_data = {
            'id_patient': ObjectId(patient_id),
            'id_medecin': medecin_id_fonctionnel,
            'date': datetime.fromisoformat(date_str),  # Conserver datetime
            'diagnostic': diagnostic,
            'prescriptions': prescriptions,
            'notes': notes
        }

        try:   
            mongo_service.insert_consultation(consultation_data)
            sync_all()
            flash("Consultation enregistrée avec succès !", "success")
            return redirect(url_for('medecin_dashboard'))
        except Exception as e:
            flash(f"Une erreur est survenue lors de l'enregistrement : {e}", "danger")
            return render_template('consultation_form.html', consultation=request.form)

    return render_template('consultation_form.html', consultation=None)



@app.route('/medecin/consultations/edit/<string:consultation_id>', methods=['GET', 'POST'])
def edit_consultation(consultation_id):
    consultation = mongo_service.get_consultation_by_id(consultation_id)
    if not consultation:
        flash("Consultation introuvable.", "danger")
        return redirect(url_for('medecin_dashboard'))

    # Récupération du patient lié à la consultation pour affichage du nom
    patient = mongo_service.get_patient_by_id(consultation['id_patient'])
    patient_name = patient['nom'] if patient else "Patient inconnu"

    if request.method == 'GET':
        return render_template('consultation_form.html', consultation=consultation, patient_name=patient_name)

    if request.method == 'POST':
        date_str = request.form.get('date', '').strip()
        diagnostic = request.form.get('diagnostic', '').strip()
        prescriptions_list = request.form.getlist('prescriptions[]')
        prescriptions = [p.strip() for p in prescriptions_list if p.strip()]
        notes = request.form.get('notes', '').strip()

        if not date_str or not diagnostic:
            flash("Veuillez remplir les champs Date et Diagnostic.", "error")
            return render_template('consultation_form.html', consultation=consultation, patient_name=patient_name, error=True)

        updated_data = {
            'date': date_str,
            'diagnostic': diagnostic,
            'prescriptions': prescriptions,
            'notes': notes
        }

        try:
            mongo_service.update_consultation(consultation_id, updated_data)
            flash("La consultation a été mise à jour avec succès.", "success")
            return redirect(url_for('medecin_dashboard'))
        except Exception as e:
            flash(f"Erreur lors de la mise à jour : {e}", "danger")
            return render_template('consultation_form.html', consultation=consultation, patient_name=patient_name)

    return redirect(url_for('medecin_dashboard'))
















if __name__ == "__main__":
    sync_all()
    app.run(debug=True, port=1000)