from flask import Blueprint, render_template, session, redirect, url_for, request, flash
from models.user_model import UserModel

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    if 'user' not in session:
        return render_template('home.html')
    return render_template('dashbord.html')

@main_bp.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect(url_for('auth.login'))
    return render_template('dashbord.html')

@main_bp.route('/list_users')
def list_users():
    if 'user' not in session:
        return redirect(url_for('auth.login'))
    if not session['user'].get('is_admin', False):
        return redirect(url_for('main.index'))  # or flash message
    users = list(UserModel.collection.find({}))
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
        success, msg = UserModel.update_user(user_email, cin=cin, nom=nom, prenoms=prenoms, fonction=fonction)
        flash(msg, "success" if success else "danger")
        if success:
            return redirect(url_for('main.list_users'))
    return render_template('edit_user.html', user=user)

@main_bp.route('/delete_user/<user_email>')
def delete_user(user_email):
    if 'user' not in session or not session['user'].get('is_admin', False):
        return redirect(url_for('main.index'))
    if user_email == session['user']['email']:
        flash("Vous ne pouvez pas vous supprimer vous-même.", "danger")
        return redirect(url_for('main.list_users'))
    success, msg = UserModel.delete_user(user_email)
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

