from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from models.message_model import MessageModel
from models.hill_cipher import hill_chiffrement_ansi_base64, hill_dechiffrement_ansi_base64
from models.chiffrement_model import base64_en_matrice, generer_matrice_inversible, matrice_en_base64
from models.key_model import KeyModel
from models.notification_model import NotificationModel

message_bp = Blueprint('message', __name__)

@message_bp.route('/send_message', methods=['POST'])
def send_message():
    if 'user' not in session:
        return redirect(url_for('auth.login'))
    
    receiver_email = request.form['receiver_email']
    message_content = request.form['message_content']
    encryption_key = request.form.get('encryption_key', '')
    sender_email = session['user']['email']
    
    # Use the stored key if no encryption key is provided
    if not encryption_key:
        stored_key = KeyModel.get_key(sender_email, receiver_email)
        if stored_key:
            # The stored key is hashed, so we need to verify it
            # For now, we will use the stored key directly (assuming it is the correct key)
            encryption_key = stored_key
        else:
            flash("Clé de chiffrement manquante et aucune clé stockée disponible.", "danger")
            return redirect(url_for('main.chat', user_email=receiver_email))
    
    # Convert the encryption key from base64 to matrix
    try:
        matrice_cle = base64_en_matrice(encryption_key)  # Let the function determine the size
    except Exception as e:
        flash(f"Erreur lors de la conversion de la clé: {str(e)}", "danger")
        return redirect(url_for('main.chat', user_email=receiver_email))
    
    # Encrypt the message using Hill cipher
    try:
        encrypted_message, original_length = hill_chiffrement_ansi_base64(matrice_cle, message_content)
    except Exception as e:
        flash(f"Erreur lors du chiffrement du message: {str(e)}", "danger")
        return redirect(url_for('main.chat', user_email=receiver_email))
    
    success, msg = MessageModel.send_message(sender_email, receiver_email, encrypted_message, is_encrypted=True)
    flash(msg, "success" if success else "danger")
    
    # Create a notification with the real key used
    NotificationModel.create_notification(sender_email, receiver_email, encryption_key)
    
    return redirect(url_for('main.chat', user_email=receiver_email))

@message_bp.route('/get_messages/<user_email>')
def get_messages(user_email):
    if 'user' not in session:
        return redirect(url_for('auth.login'))
    
    current_user_email = session['user']['email']
    messages = MessageModel.get_messages(current_user_email, user_email)
    return jsonify([
        {
            "sender_email": msg['sender_email'],
            "receiver_email": msg['receiver_email'],
            "message_content": msg['message_content'],
            "is_encrypted": msg.get('is_encrypted', False),
            "timestamp": msg['timestamp'].strftime('%Y-%m-%d %H:%M:%S')
        }
        for msg in messages
    ])

@message_bp.route('/decrypt_message', methods=['POST'])
def decrypt_message():
    if 'user' not in session:
        return redirect(url_for('auth.login'))
    
    data = request.get_json()
    encrypted_message = data.get('encrypted_message')
    encryption_key = data.get('encryption_key')
    
    if not encrypted_message or not encryption_key:
        return jsonify({"success": False, "error": "Message chiffré ou clé manquante"})
    
    # Convert the encryption key from base64 to matrix
    try:
        matrice_cle = base64_en_matrice(encryption_key)  # Let the function determine the size
    except Exception as e:
        return jsonify({"success": False, "error": f"Erreur lors de la conversion de la clé: {str(e)}"})
    
    # Decrypt the message using Hill cipher
    try:
        decrypted_message = hill_dechiffrement_ansi_base64(matrice_cle, encrypted_message)
        return jsonify({"success": True, "decrypted_message": decrypted_message})
    except Exception as e:
        return jsonify({"success": False, "error": f"Erreur lors du déchiffrement du message: {str(e)}"})


@message_bp.route('/generate_key', methods=['GET'])
def generate_key():
    if 'user' not in session:
        return redirect(url_for('auth.login'))
    
    # Get the size parameter from the request (default to 5)
    taille = int(request.args.get('size', 5))
    
    # Get the receiver_email parameter from the request
    receiver_email = request.args.get('receiver_email', '')
    
    # Validate that the size is one of the allowed values
    if taille not in [5, 15, 50]:
        return jsonify({"success": False, "error": "Taille de matrice non supportée. Utilisez 5, 15 ou 50."})
    
    try:
        matrice = generer_matrice_inversible(taille)
        matrice_base64 = matrice_en_base64(matrice)
        
        # Store the key for the pair of users if receiver_email is provided
        if receiver_email:
            sender_email = session['user']['email']
            KeyModel.store_key(sender_email, receiver_email, matrice_base64)
        
        return jsonify({"success": True, "key": matrice_base64, "size": taille})
    except Exception as e:
        return jsonify({"success": False, "error": f"Erreur lors de la génération de la clé: {str(e)}"})

@message_bp.route('/get_stored_key', methods=['GET'])
def get_stored_key():
    if 'user' not in session:
        return redirect(url_for('auth.login'))
    
    # Get the receiver_email parameter from the request
    receiver_email = request.args.get('receiver_email', '')
    
    if not receiver_email:
        return jsonify({"success": False, "error": "Email du destinataire manquant."})
    
    try:
        sender_email = session['user']['email']
        # Get the stored key from the KeyModel
        stored_key = KeyModel.get_key(sender_email, receiver_email)
         
        if stored_key:
            return jsonify({"success": True, "key": stored_key})
        else:
            return jsonify({"success": False, "error": "Aucune clé stockée trouvée pour cette paire d'utilisateurs."})
    except Exception as e:
        return jsonify({"success": False, "error": f"Erreur lors de la récupération de la clé: {str(e)}"})


@message_bp.route('/get_all_stored_keys', methods=['GET'])
def get_all_stored_keys():
    if 'user' not in session:
        return redirect(url_for('auth.login'))
    
    try:
        user_email = session['user']['email']
        # Get all keys for the user from the KeyModel
        keys = KeyModel.get_all_keys_for_user(user_email)
        
        return jsonify({"success": True, "keys": keys})
    except Exception as e:
        return jsonify({"success": False, "error": f"Erreur lors de la récupération des clés: {str(e)}"})


@message_bp.route('/notifications')
def notifications():
    if 'user' not in session:
        return redirect(url_for('auth.login'))
    
    return render_template('notification.html')


@message_bp.route('/get_notifications', methods=['GET'])
def get_notifications():
    if 'user' not in session:
        return redirect(url_for('auth.login'))
    
    # Récupérer les notifications réelles pour l'utilisateur actuel
    user_email = session['user']['email']
    notifications = NotificationModel.get_notifications_for_user(user_email)
    
    # Formater les notifications pour l'affichage
    formatted_notifications = []
    for notification in notifications:
        # Utiliser la clé originale inversée depuis la notification
        original_key = notification.get("original_key", notification["key_used"][::-1])
        
        formatted_notification = {
            "sender": notification["sender_email"],
            "key": original_key,  # Afficher la clé originale
            "timestamp": notification["timestamp"].strftime('%Y-%m-%d %H:%M:%S'),
            "is_read": notification["is_read"]
        }
        formatted_notifications.append(formatted_notification)
    
    return jsonify({"success": True, "notifications": formatted_notifications})
    
    