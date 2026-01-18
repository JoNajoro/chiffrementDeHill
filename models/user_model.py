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
            "fonction": fonction,
            "approved": False  # Par défaut, l'utilisateur est en attente d'approbation
        }

        UserModel.collection.insert_one(user)
        return True, "Utilisateur enregistré avec succès."

    @staticmethod
    def get_user_by_email(email):
        """Récupère un utilisateur par son email."""
        return UserModel.collection.find_one({"email": email})

    @staticmethod
    def login(email, password):
        user = UserModel.collection.find_one({"email": email})
        if user and check_password_hash(user["password"], password):
            if not (user.get("approved", False) or user.get("is_approved", False)):
                return False, "Votre compte est en attente d'approbation par l'administrateur."
            return True, user
        return False, "Email ou mot de passe incorrect."

    @staticmethod
    def update_user(email, cin=None, nom=None, prenoms=None, fonction=None, avatar=None):
        update_data = {}
        if cin is not None:
            update_data['cin'] = cin
        if nom is not None:
            update_data['nom'] = nom
        if prenoms is not None:
            update_data['prenoms'] = prenoms
        if fonction is not None:
            update_data['fonction'] = fonction
        if avatar is not None:
            update_data['avatar'] = avatar
        if update_data:
            UserModel.collection.update_one({"email": email}, {"$set": update_data})
            return True, "Utilisateur mis à jour avec succès."
        return False, "Aucune donnée à mettre à jour."

    @staticmethod
    def delete_user(email):
        result = UserModel.collection.delete_one({"email": email})
        if result.deleted_count > 0:
            return True, "Utilisateur supprimé avec succès."
        return False, "Utilisateur non trouvé."

    @staticmethod
    def approve_user(email):
        result = UserModel.collection.update_one({"email": email}, {"$set": {"approved": True}})
        if result.modified_count > 0:
            return True, "Utilisateur approuvé avec succès."
        return False, "Utilisateur non trouvé ou déjà approuvé."

    @staticmethod
    def reject_user(email):
        result = UserModel.collection.delete_one({"email": email})
        if result.deleted_count > 0:
            return True, "Utilisateur rejeté et supprimé avec succès."
        return False, "Utilisateur non trouvé."

    @staticmethod
    def get_pending_users():
        # Users that are not approved (neither 'approved' nor 'is_approved' is True)
        return list(UserModel.collection.find({
            "$and": [
                {"$or": [{"approved": {"$ne": True}}, {"approved": {"$exists": False}}]},
                {"$or": [{"is_approved": {"$ne": True}}, {"is_approved": {"$exists": False}}]}
            ]
        }))
