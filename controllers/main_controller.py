from flask import Blueprint, render_template, session, redirect, url_for, request, flash, jsonify, send_from_directory
from models.user_model import UserModel
from bson import ObjectId
import os
from werkzeug.utils import secure_filename

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    if 'user' not in session:
        return render_template('home.html')
    # Récupérer tous les utilisateurs pour le dashboard
    all_users = list(UserModel.collection.find({}))
    return render_template('dashbord.html', all_users=all_users)

@main_bp.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect(url_for('auth.login'))
    # Récupérer tous les utilisateurs pour le dashboard
    all_users = list(UserModel.collection.find({}))
    return render_template('dashbord.html', all_users=all_users)

@main_bp.route('/list_users')
def list_users():
    if 'user' not in session:
        return redirect(url_for('auth.login'))
    # Tous les utilisateurs approuvés peuvent voir la liste des utilisateurs
    if not (session['user'].get('approved', False) or session['user'].get('is_approved', False)):
        flash("Votre compte doit être approuvé pour accéder à cette fonctionnalité.", "warning")
        return redirect(url_for('main.index'))
    users = list(UserModel.collection.find({}))
    # Debug: Afficher le nombre d'utilisateurs et leur statut
    approved_count = sum(1 for user in users if user.get('approved', False))
    print(f"Total utilisateurs: {len(users)}, Approuvés: {approved_count}")
    for user in users:
        print(f"- {user['email']}: {'Approuvé' if user.get('approved', False) else 'En attente'}")
    return render_template('list_users.html', users=users)

@main_bp.route('/edit_user/<user_email>', methods=['GET', 'POST'])
def edit_user(user_email):
    if 'user' not in session or not session['user'].get('is_admin', False):
        return redirect(url_for('main.index'))
    user = UserModel.get_user_by_email(user_email)
    if not user:
        flash("Utilisateur non trouvé.", "danger")
        return redirect(url_for('main.list_users'))
    if request.method == 'POST':
        cin = request.form['cin']
        nom = request.form['nom']
        prenoms = request.form['prenoms']
        fonction = request.form['fonction']

        # Validation du CIN : doit faire exactement 12 chiffres
        if not cin or len(cin) != 12 or not cin.isdigit():
            flash("Le CIN doit contenir exactement 12 chiffres.", "danger")
            return redirect(url_for('main.edit_user', user_email=user_email))

        success, msg = UserModel.update_user(user_email, cin=cin, nom=nom, prenoms=prenoms, fonction=fonction)
        flash(msg, "success" if success else "danger")
        if success:
            return redirect(url_for('main.list_users'))
    return render_template('edit_user.html', user=user)

@main_bp.route('/delete_user/<user_email>', methods=['GET', 'POST'])
def delete_user(user_email):
    if 'user' not in session or not session['user'].get('is_admin', False):
        if request.method == 'POST':
            return jsonify({'success': False, 'message': 'Non autorisé'}), 403
        return redirect(url_for('main.index'))
    if user_email == session['user']['email']:
        if request.method == 'POST':
            return jsonify({'success': False, 'message': 'Vous ne pouvez pas vous supprimer vous-même.'}), 400
        flash("Vous ne pouvez pas vous supprimer vous-même.", "danger")
        return redirect(url_for('main.list_users'))
    success, msg = UserModel.delete_user(user_email)
    if request.method == 'POST':
        return jsonify({'success': success, 'message': msg})
    flash(msg, "success" if success else "danger")
    return redirect(url_for('main.list_users'))

@main_bp.route('/chat/<user_email>')
def chat(user_email):
    if 'user' not in session:
        return redirect(url_for('auth.login'))
    return render_template('chat.html', user_email=user_email)

@main_bp.route('/pending_users')
def pending_users():
    if 'user' not in session:
        return redirect(url_for('auth.login'))
    if not session['user'].get('is_admin', False):
        return redirect(url_for('main.index'))  # or flash message
    pending_users_list = UserModel.get_pending_users()
    return render_template('pending_users.html', pending_users=pending_users_list)

@main_bp.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory('uploads', filename)

@main_bp.route('/upload_avatar', methods=['POST'])
def upload_avatar():
    if 'user' not in session:
        return jsonify({'success': False, 'message': 'Non autorisé'}), 401

    if 'avatar' not in request.files:
        return jsonify({'success': False, 'message': 'Aucun fichier fourni'}), 400

    file = request.files['avatar']
    if file.filename == '':
        return jsonify({'success': False, 'message': 'Aucun fichier sélectionné'}), 400

    if file and file.filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
        filename = secure_filename(file.filename)
        # Create unique filename with user email
        user_email = session['user']['email']
        name, ext = os.path.splitext(filename)
        unique_filename = f"{user_email}_{name}{ext}"
        filepath = os.path.join('uploads', unique_filename)

        # Ensure uploads directory exists
        os.makedirs('uploads', exist_ok=True)

        file.save(filepath)

        # Update user avatar in database
        avatar_url = f"/uploads/{unique_filename}"
        UserModel.update_user(user_email, avatar=avatar_url)

        # Update session
        session['user']['avatar'] = avatar_url
        session.modified = True

        return jsonify({'success': True, 'avatar_url': avatar_url})
    else:
        return jsonify({'success': False, 'message': 'Type de fichier non autorisé'}), 400

