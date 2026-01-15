from config.mongo_client import db
from datetime import datetime
import os
from models.crypto_utils import encrypt_file_bytes, decrypt_file_bytes

class FileModel:
    collection = db['files']

    @staticmethod
    def send_file(sender_email, receiver_email, file_path, encryption_key, original_filename):
        # Lire le contenu du fichier
        with open(file_path, 'rb') as file:
            file_content = file.read()

        # Chiffrer le contenu du fichier
        encrypted_file_content = encrypt_file_bytes(file_content, encryption_key)

        # Stocker les métadonnées du fichier dans la base de données
        file_metadata = {
            "sender_email": sender_email,
            "receiver_email": receiver_email,
            "original_filename": original_filename,
            "file_content": encrypted_file_content,
            "encryption_key": encryption_key,
            "timestamp": datetime.now()
        }
        FileModel.collection.insert_one(file_metadata)
        return True, "Fichier envoyé avec succès."

    @staticmethod
    def get_files(user1_email, user2_email):
        files = list(FileModel.collection.find({
            "$or": [
                {
                    "sender_email": user1_email,
                    "receiver_email": user2_email
                },
                {
                    "sender_email": user2_email,
                    "receiver_email": user1_email
                }
            ]
        }).sort("timestamp", 1))
        
        # Ne pas déchiffrer le contenu des fichiers ici, laisser le contenu chiffré
        # Le déchiffrement sera fait côté client avec la clé fournie par l'utilisateur
        return files