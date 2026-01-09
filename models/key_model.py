from config.mongo_client import db
import hashlib

class KeyModel:
    collection = db['cle']

    @staticmethod
    def hash_key(key):
        """
        Hash the encryption key using SHA-256.
        """
        return hashlib.sha256(key.encode()).hexdigest()

    @staticmethod
    def store_key(user1_email, user2_email, key):
        """
        Store the encryption key for a pair of users in the database.
        The key is hashed before storing.
        """
        hashed_key = KeyModel.hash_key(key)
        
        # Ensure the users are ordered to avoid duplicate entries
        users = sorted([user1_email, user2_email])
        
        key_document = {
            "user1_email": users[0],
            "user2_email": users[1],
            "hashed_key": hashed_key
        }
        
        # Insert or update the key document
        KeyModel.collection.update_one(
            {
                "user1_email": users[0],
                "user2_email": users[1]
            },
            {"$set": key_document},
            upsert=True
        )
        
        return True, "Clé stockée avec succès."

    @staticmethod
    def get_key(user1_email, user2_email):
        """
        Retrieve the hashed encryption key for a pair of users.
        """
        # Ensure the users are ordered to avoid duplicate entries
        users = sorted([user1_email, user2_email])
        
        key_document = KeyModel.collection.find_one(
            {
                "user1_email": users[0],
                "user2_email": users[1]
            }
        )
        
        if key_document:
            return key_document["hashed_key"]  # Return the hashed key
        else:
            return None

    @staticmethod
    def verify_key(user1_email, user2_email, key):
        """
        Verify if the provided key matches the stored hashed key for a pair of users.
        """
        stored_hashed_key = KeyModel.get_key(user1_email, user2_email)
        
        if stored_hashed_key:
            hashed_key = KeyModel.hash_key(key)
            return hashed_key == stored_hashed_key
        else:
            return False

    @staticmethod
    def get_all_keys_for_user(user_email):
        """
        Retrieve all keys associated with a specific user.
        """
        keys = []
        
        # Find all keys where the user is either user1 or user2
        key_documents = KeyModel.collection.find({
            "$or": [
                {"user1_email": user_email},
                {"user2_email": user_email}
            ]
        })
        
        for doc in key_documents:
            # Determine the receiver email (the other user in the pair)
            receiver_email = doc["user2_email"] if doc["user1_email"] == user_email else doc["user1_email"]
            
            keys.append({
                "receiver_email": receiver_email,
                "key": doc["hashed_key"]
            })
        
        return keys