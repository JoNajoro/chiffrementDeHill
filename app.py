from flask import Flask
from controllers.auth_controller import auth_bp
from controllers.main_controller import main_bp
from controllers.message_controller import message_bp
from controllers.document_controller import document_bp
from controllers.notification_controller import notification_bp

app = Flask(__name__)
app.secret_key = "2525"  # À remplacer par une vraie clé sécurisée

# Enregistrement des Blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(main_bp)
app.register_blueprint(message_bp)
app.register_blueprint(document_bp)
app.register_blueprint(notification_bp)

if __name__ == "__main__":
    # Pour accéder depuis d'autres appareils sur le réseau :
    # host='0.0.0.0' permet d'écouter sur toutes les interfaces réseau
    # port=5000 est le port par défaut de Flask
    app.run(debug=True, host='0.0.0.0', port=5000)

from datetime import timedelta

app.config.update(
    SESSION_COOKIE_SECURE=True,      # HTTPS obligatoire (Render est HTTPS)
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE='None',   # TRÈS IMPORTANT pour Chrome
    PERMANENT_SESSION_LIFETIME=timedelta(days=1)
)
