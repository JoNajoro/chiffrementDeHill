from config.mongo_client import db
from datetime import datetime

class MessageModel:
    collection = db['messages']

    @staticmethod
    def send_message(sender_email, receiver_email, message_content):
        message = {
            "sender_email": sender_email,
            "receiver_email": receiver_email,
            "message_content": message_content,
            "timestamp": datetime.now()
        }
        MessageModel.collection.insert_one(message)
        return True, "Message envoyé avec succès."

    @staticmethod
    def get_messages(user1_email, user2_email):
        messages = list(MessageModel.collection.find({
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
        return messages