from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify, make_response
from models.user_model import UserModel

auth_bp = Blueprint('auth', __name__)

# Page d'inscription
@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        cin = request.form['cin']
        nom = request.form['nom']
        prenoms = request.form['prenoms']
        email = request.form['email']
        password = request.form['password']
        password2 = request.form['password2']
        fonction = request.form['fonction']

        if password != password2:
            flash("Les mots de passe ne correspondent pas.", "danger")
            return redirect(url_for('auth.register'))

        success, msg = UserModel.register(cin, nom, prenoms, email, password, fonction)
        flash(msg, "success" if success else "danger")
        if success:
            return redirect(url_for('auth.login'))

    return render_template('register.html')

# Page de connexion
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        success, user_or_msg = UserModel.login(email, password)
        if success:
            is_admin = (email == 'najorojoelson@gmail.com')
            session['user'] = {
                "cin": user_or_msg['cin'],
                "nom": user_or_msg['nom'],
                "prenoms": user_or_msg['prenoms'],
                "email": user_or_msg['email'],
                "fonction": user_or_msg['fonction'],
                "is_admin": is_admin
            }
            flash("Connexion réussie !", "success")
            if is_admin:
                flash("Bienvenue Administrateur ! Vous avez accès aux fonctionnalités de gestion des utilisateurs.", "info")
            return redirect(url_for('main.index'))
        else:
            flash(user_or_msg, "danger")
            return redirect(url_for('auth.login'))

    # Ajouter des headers pour empêcher le cache
    response = make_response(render_template('login.html'))
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

# Déconnexion
@auth_bp.route('/logout')
def logout():
    session.pop('user', None)
    session.pop('locked', None)
    flash("Déconnecté.", "success")
    return redirect(url_for('main.index'))

# Verrouiller la session (appelé par le client quand le chrono atteint 00:00)
@auth_bp.route('/lock', methods=['POST'])
def lock():
    if 'user' not in session:
        return jsonify({'success': False, 'message': 'Session expirée'}), 401

    session['locked'] = True
    return jsonify({'success': True})

# Vérifier l'état de verrouillage de la session
@auth_bp.route('/check_lock')
def check_lock():
    logged_in = 'user' in session
    locked = session.get('locked', False)
    return jsonify({'logged_in': logged_in, 'locked': locked})

# Déverrouiller la session
@auth_bp.route('/unlock', methods=['POST'])
def unlock():
    if 'user' not in session:
        return jsonify({'success': False, 'message': 'Session expirée'}), 401

    data = request.get_json()
    password = data.get('password')
    if not password:
        return jsonify({'success': False, 'message': 'Mot de passe requis'})

    # Vérifier le mot de passe
    success, user_or_msg = UserModel.login(session['user']['email'], password)
    if success:
        session['locked'] = False
        return jsonify({'success': True})
    else:
        return jsonify({'success': False, 'message': 'Mot de passe incorrect'})

# Approuver un utilisateur
@auth_bp.route('/approve_user/<email>', methods=['POST'])
def approve_user(email):
    if 'user' not in session or not session['user'].get('is_admin', False):
        return jsonify({'success': False, 'message': 'Accès non autorisé'}), 403

    success, msg = UserModel.approve_user(email)
    if success:
        # Envoyer une notification à l'utilisateur approuvé
        from models.approval_notification_model import ApprovalNotificationModel
        admin_email = session['user']['email']
        message = f"Votre compte a été approuvé par l'administrateur {admin_email}."
        ApprovalNotificationModel.create_approval_notification(email, admin_email, message)
        return jsonify({'success': True, 'message': msg})
    else:
        return jsonify({'success': False, 'message': msg})

# Rejeter un utilisateur
@auth_bp.route('/reject_user/<email>', methods=['POST'])
def reject_user(email):
    if 'user' not in session or not session['user'].get('is_admin', False):
        return jsonify({'success': False, 'message': 'Accès non autorisé'}), 403

    success, msg = UserModel.reject_user(email)
    if success:
        # Envoyer une notification de rejet
        from models.approval_notification_model import ApprovalNotificationModel
        admin_email = session['user']['email']
        message = f"Votre demande d'inscription a été rejetée par l'administrateur {admin_email}."
        ApprovalNotificationModel.create_approval_notification(email, admin_email, message)
        return jsonify({'success': True, 'message': msg})
    else:
        return jsonify({'success': False, 'message': msg})


