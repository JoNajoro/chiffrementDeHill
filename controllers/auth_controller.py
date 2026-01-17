from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
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
            session['user'] = {
                "cin": user_or_msg['cin'],
                "nom": user_or_msg['nom'],
                "prenoms": user_or_msg['prenoms'],
                "email": user_or_msg['email'],
                "fonction": user_or_msg['fonction']
            }
            flash("Connexion réussie !", "success")
            return redirect(url_for('main.index'))
        else:
            flash(user_or_msg, "danger")
            return redirect(url_for('auth.login'))

    return render_template('login.html')

# Déconnexion
@auth_bp.route('/logout')
def logout():
    session.pop('user', None)
    flash("Déconnecté.", "success")
    return redirect(url_for('auth.login'))

# Déverrouillage de session
@auth_bp.route('/unlock', methods=['POST'])
def unlock():
    if 'user' not in session:
        return jsonify({'success': False, 'message': 'Session expirée'}), 401

    data = request.get_json()
    password = data.get('password')

    if not password:
        return jsonify({'success': False, 'message': 'Mot de passe requis'}), 400

    # Vérifier le mot de passe de l'utilisateur actuel
    email = session['user']['email']
    success, user_or_msg = UserModel.login(email, password)

    if success:
        return jsonify({'success': True})
    else:
        return jsonify({'success': False, 'message': 'Mot de passe incorrect'}), 401
