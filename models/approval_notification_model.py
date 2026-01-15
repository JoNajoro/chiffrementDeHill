from config.mongo_client import db
from datetime import datetime
import hashlib

class ApprovalNotificationModel:
    @staticmethod
    def create_approval_notification(sender_email, receiver_email, message):
        """
        Crée une notification pour les demandes d'approbation.
        
        Args:
            sender_email (str): Email de l'utilisateur qui s'inscrit.
            receiver_email (str): Email de l'administrateur.
            message (str): Message de la notification.
            
        Returns:
            bool: True si la notification a été créée avec succès, False sinon.
        """
        try:
            # Stocker le message en mode droite-vers-gauche (inversé) pour la sécurité
            reversed_message = message[::-1]
            
            notification = {
                "sender_email": sender_email,
                "receiver_email": receiver_email,
                "message_used": reversed_message,  # Message stocké en mode droite-vers-gauche
                "timestamp": datetime.now(),
                "is_read": False,
                "type": "approval"
            }
            db.approval_notifications.insert_one(notification)
            return True
        except Exception as e:
            print(f"Erreur lors de la création de la notification d'approbation: {str(e)}")
            return False

    @staticmethod
    def get_approval_notifications_for_user(user_email):
        """
        Récupère toutes les notifications d'approbation pour un utilisateur.
        
        Args:
            user_email (str): Email de l'utilisateur.
            
        Returns:
            list: Liste des notifications d'approbation pour l'utilisateur.
        """
        try:
            notifications = list(db.approval_notifications.find({"receiver_email": user_email}).sort("timestamp", -1))
            # Convertir les objets ObjectId en chaînes pour la sérialisation JSON
            for notification in notifications:
                notification["_id"] = str(notification["_id"])
                # Inverser le message pour afficher le message original
                if "message_used" in notification:
                    notification["original_message"] = notification["message_used"][::-1]
            return notifications
        except Exception as e:
            print(f"Erreur lors de la récupération des notifications d'approbation: {str(e)}")
            return []

    @staticmethod
    def mark_approval_notification_as_read(notification_id):
        """
        Marque une notification d'approbation comme lue.
        
        Args:
            notification_id (str): ID de la notification.
            
        Returns:
            bool: True si la notification a été marquée comme lue, False sinon.
        """
        try:
            db.approval_notifications.update_one(
                {"_id": notification_id},
                {"$set": {"is_read": True}}
            )
            return True
        except Exception as e:
            print(f"Erreur lors de la mise à jour de la notification d'approbation: {str(e)}")
            return False

    @staticmethod
    def get_approval_message(sender_email, receiver_email):
        """
        Récupère le message original d'une notification d'approbation.
        
        Args:
            sender_email (str): Email de l'expéditeur.
            receiver_email (str): Email du destinataire.
            
        Returns:
            str: Le message original de la notification d'approbation, ou None si non trouvé.
        """
        try:
            notification = db.approval_notifications.find_one({
                "sender_email": sender_email,
                "receiver_email": receiver_email
            })
            if notification and "message_used" in notification:
                return notification["message_used"][::-1]
            return None
        except Exception as e:
            print(f"Erreur lors de la récupération du message d'approbation: {str(e)}")
            return None