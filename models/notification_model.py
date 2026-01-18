from config.mongo_client import db
from datetime import datetime
import hashlib

class NotificationModel:
    @staticmethod
    def create_notification(sender_email, receiver_email, key_used):
        """
        Crée une notification pour le destinataire avec la clé utilisée (en mode droite-vers-gauche).
        
        Args:
            sender_email (str): Email de l'expéditeur.
            receiver_email (str): Email du destinataire.
            key_used (str): Clé utilisée pour le chiffrement.
        
        Returns:
            bool: True si la notification a été créée avec succès, False sinon.
        """
        try:
            # Stocker la clé en mode droite-vers-gauche (inversé)
            reversed_key = key_used[::-1]
            
            notification = {
                "sender_email": sender_email,
                "receiver_email": receiver_email,
                "key_used": reversed_key,  # Clé stockée en mode droite-vers-gauche
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
                # Inverser la clé pour afficher la clé originale (la clé est stockée en mode droite-vers-gauche)
                if "key_used" in notification:
                    notification["original_key"] = notification["key_used"][::-1]
                # Formater le timestamp pour l'affichage
                if "timestamp" in notification and hasattr(notification["timestamp"], 'strftime'):
                    notification["timestamp"] = notification["timestamp"].strftime('%Y-%m-%d %H:%M:%S')
            return notifications
        except Exception as e:
            print(f"Erreur lors de la récupération des notifications: {str(e)}")
            return []

    @staticmethod
    def toggle_notification_read(notification_id):
        """
        Bascule le statut lu/non lu d'une notification.

        Args:
            notification_id (ObjectId): ID de la notification.

        Returns:
            bool: True si la notification a été mise à jour, False sinon.
        """
        try:
            # Récupérer la notification actuelle
            notification = db.notifications.find_one({"_id": notification_id})
            if not notification:
                return False

            # Inverser le statut is_read
            new_read_status = not notification.get("is_read", False)

            db.notifications.update_one(
                {"_id": notification_id},
                {"$set": {"is_read": new_read_status}}
            )
            return True
        except Exception as e:
            print(f"Erreur lors de la mise à jour de la notification: {str(e)}")
            return False

    @staticmethod
    def delete_notification(notification_id, user_email):
        """
        Supprime une notification pour un utilisateur spécifique.

        Args:
            notification_id (str): ID de la notification.
            user_email (str): Email de l'utilisateur pour vérification.

        Returns:
            bool: True si la notification a été supprimée, False sinon.
        """
        try:
            result = db.notifications.delete_one({
                "_id": notification_id,
                "receiver_email": user_email
            })
            return result.deleted_count > 0
        except Exception as e:
            print(f"Erreur lors de la suppression de la notification: {str(e)}")
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
            stored_key = KeyModel.get_key(sender_email, receiver_email)
            if stored_key:
                # Si la clé est stockée en mode droite-vers-gauche, l'inverser pour obtenir la clé originale
                # Mais pour l'instant, nous ne changeons pas le stockage des clés dans KeyModel
                return stored_key
            return None
        except Exception as e:
            print(f"Erreur lors de la récupération de la clé originale: {str(e)}")
            return None
