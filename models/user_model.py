from config.mongo_client import db
from werkzeug.security import generate_password_hash, check_password_hash

class UserModel:
    collection = db['utilisateurs']

    @staticmethod
    def register(cin, nom, prenoms, email, password, fonction):
        # Vérifier si l'email existe déjà
        if UserModel.collection.find_one({"email": email}):
            return False, "Email déjà utilisé."

        # Hash du mot de passe
        hashed_password = generate_password_hash(password)

        # Création de l'utilisateur
        user = {
            "cin": cin,
            "nom": nom,
            "prenoms": prenoms,
            "email": email,
            "password": hashed_password,
            "fonction": fonction
        }

        UserModel.collection.insert_one(user)
        return True, "Utilisateur enregistré avec succès."

    @staticmethod
    def login(email, password):
        user = UserModel.collection.find_one({"email": email})
        if user and check_password_hash(user["password"], password):
            return True, user
        return False, "Email ou mot de passe incorrect."
