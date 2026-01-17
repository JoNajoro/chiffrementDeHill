from flask import Flask
from controllers.auth_controller import auth_bp
from controllers.main_controller import main_bp
from controllers.message_controller import message_bp
from controllers.document_controller import document_bp

app = Flask(__name__)
app.secret_key = "ton_secret_key"  # À remplacer par une vraie clé sécurisée

# Enregistrement des Blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(main_bp)
app.register_blueprint(message_bp)
app.register_blueprint(document_bp)

if __name__ == "__main__":
    # Pour accéder depuis d'autres appareils sur le réseau :
    # host='0.0.0.0' permet d'écouter sur toutes les interfaces réseau
    # port=5000 est le port par défaut de Flask
    app.run(debug=True, host='0.0.0.0', port=5000)
