from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from models.message_model import MessageModel
from models.hill_cipher import hill_chiffrement_ansi_base64, hill_dechiffrement_ansi_base64
from models.chiffrement_model import base64_en_matrice, generer_matrice_inversible, matrice_en_base64

message_bp = Blueprint('message', __name__)

@message_bp.route('/send_message', methods=['POST'])
def send_message():
    if 'user' not in session:
        return redirect(url_for('auth.login'))
    
    receiver_email = request.form['receiver_email']
    message_content = request.form['message_content']
    encryption_key = request.form['encryption_key']
    sender_email = session['user']['email']
    
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
    
    # Validate that the size is one of the allowed values
    if taille not in [5, 15, 50]:
        return jsonify({"success": False, "error": "Taille de matrice non supportée. Utilisez 5, 15 ou 50."})
    
    try:
        matrice = generer_matrice_inversible(taille)
        matrice_base64 = matrice_en_base64(matrice)
        return jsonify({"success": True, "key": matrice_base64, "size": taille})
    except Exception as e:
        return jsonify({"success": False, "error": f"Erreur lors de la génération de la clé: {str(e)}"})
    
    