from flask import Blueprint, jsonify, request, session
from models.notification_model import NotificationModel
from models.user_model import UserModel  # Vérification mot de passe
from bson import ObjectId

notification_bp = Blueprint('notification', __name__)

@notification_bp.route('/get_notifications', methods=['GET'])
def get_notifications():
    if 'user' not in session:
        return jsonify({"success": False, "error": "Utilisateur non connecté."})

    user_email = session['user']['email']
    notifications = NotificationModel.get_notifications_for_user(user_email)
    return jsonify({"success": True, "notifications": notifications})

@notification_bp.route('/verify_password', methods=['POST'])
def verify_password():
    if 'user' not in session:
        return jsonify({"success": False, "error": "Utilisateur non connecté."})

    data = request.get_json()
    password = data.get('password')
    user_email = session['user']['email']

    if UserModel.verify_password(user_email, password):
        return jsonify({"success": True})
    else:
        return jsonify({"success": False})

@notification_bp.route('/toggle_read/<notification_id>', methods=['POST'])
def toggle_notification_read(notification_id):
    if 'user' not in session:
        return jsonify({"success": False, "error": "Utilisateur non connecté."})

    try:
        success = NotificationModel.toggle_notification_read(ObjectId(notification_id))
        return jsonify({"success": success})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@notification_bp.route('/delete/<notification_id>', methods=['DELETE'])
def delete_notification(notification_id):
    if 'user' not in session:
        return jsonify({"success": False, "error": "Utilisateur non connecté."})

    user_email = session['user']['email']
    try:
        success = NotificationModel.delete_notification(ObjectId(notification_id), user_email)
        return jsonify({"success": success})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})
