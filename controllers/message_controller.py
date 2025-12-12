from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from models.message_model import MessageModel

message_bp = Blueprint('message', __name__)

@message_bp.route('/send_message', methods=['POST'])
def send_message():
    if 'user' not in session:
        return redirect(url_for('auth.login'))
    
    receiver_email = request.form['receiver_email']
    message_content = request.form['message_content']
    sender_email = session['user']['email']
    
    success, msg = MessageModel.send_message(sender_email, receiver_email, message_content)
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
            "timestamp": msg['timestamp'].strftime('%Y-%m-%d %H:%M:%S')
        }
        for msg in messages
    ])
    
    