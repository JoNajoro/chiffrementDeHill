from config.mongo_client import db
from datetime import datetime
import hashlib

class NotificationModel:
    @staticmethod
    def create_notification(sender_email, receiver_email, key_used):
        """
        Crée une notification pour le destinataire avec la clé utilisée (hachée uniquement).
        
        Args:
            sender_email (str): Email de l'expéditeur.
            receiver_email (str): Email du destinataire.
            key_used (str): Clé utilisée pour le chiffrement.
        
        Returns:
            bool: True si la notification a été créée avec succès, False sinon.
        """
        try:
            # Hacher la clé pour des raisons de sécurité
            hashed_key = hashlib.sha256(key_used.encode()).hexdigest()
            
            notification = {
                "sender_email": sender_email,
                "receiver_email": receiver_email,
                "key_used": hashed_key,  # Seule la clé hachée est stockée
                "timestamp": datetime.now(),
                "is_read": False
            }
            db.notifications.insert_one(notification)
            return True
        except Exception as e:
            print(f"Erreur lors de la création de la notification: {str(e)}")
            return False

    @staticmethod
    def get_notifications_for_user(user_email):
        """
        Récupère toutes les notifications pour un utilisateur.
        
        Args:
            user_email (str): Email de l'utilisateur.
        
        Returns:
            list: Liste des notifications pour l'utilisateur.
        """
        try:
            notifications = list(db.notifications.find({"receiver_email": user_email}).sort("timestamp", -1))
            # Convertir les objets ObjectId en chaînes pour la sérialisation JSON
            for notification in notifications:
                notification["_id"] = str(notification["_id"])
            return notifications
        except Exception as e:
            print(f"Erreur lors de la récupération des notifications: {str(e)}")
            return []

    @staticmethod
    def mark_notification_as_read(notification_id):
        """
        Marque une notification comme lue.
        
        Args:
            notification_id (str): ID de la notification.
        
        Returns:
            bool: True si la notification a été marquée comme lue, False sinon.
        """
        try:
            db.notifications.update_one(
                {"_id": notification_id},
                {"$set": {"is_read": True}}
            )
            return True
        except Exception as e:
            print(f"Erreur lors de la mise à jour de la notification: {str(e)}")
            return False

    @staticmethod
    def get_original_key(sender_email, receiver_email):
        """
        Récupère la clé originale utilisée pour le chiffrement entre deux utilisateurs.
        
        Args:
            sender_email (str): Email de l'expéditeur.
            receiver_email (str): Email du destinataire.
        
        Returns:
            str: La clé originale utilisée pour le chiffrement, ou None si non trouvée.
        """
        try:
            # Récupérer la clé originale depuis le modèle de clé
            original_key = KeyModel.get_key(sender_email, receiver_email)
            return original_key
        except Exception as e:
            print(f"Erreur lors de la récupération de la clé originale: {str(e)}")
            return None