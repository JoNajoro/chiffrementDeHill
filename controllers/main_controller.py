from flask import Blueprint, render_template, session, redirect, url_for, request
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
    users = list(UserModel.collection.find({}))
    return render_template('list_users.html', users=users)

@main_bp.route('/chat/<user_email>')
def chat(user_email):
    if 'user' not in session:
        return redirect(url_for('auth.login'))
    return render_template('chat.html', user_email=user_email)

