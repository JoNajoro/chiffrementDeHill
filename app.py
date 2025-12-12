from flask import Flask
from controllers.auth_controller import auth_bp
from controllers.main_controller import main_bp
from controllers.message_controller import message_bp

app = Flask(__name__)
app.secret_key = "ton_secret_key"  # À remplacer par une vraie clé sécurisée

# Enregistrement des Blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(main_bp)
app.register_blueprint(message_bp)

if __name__ == "__main__":
    app.run(debug=True)
