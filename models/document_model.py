from config.mongo_client import db
from datetime import datetime
from bson import ObjectId
import secrets
import base64

class DocumentModel:
    """Model for managing user documents with access key security."""
    
    collection = db['user_documents']
    access_keys_collection = db['document_access_keys']
    
    @staticmethod
    def generate_access_key():
        """
        Generate a secure random access key for document access.
        
        Returns:
            str: A secure random key encoded in base64.
        """
        # Generate 32 random bytes and encode to base64
        random_bytes = secrets.token_bytes(32)
        access_key = base64.urlsafe_b64encode(random_bytes).decode('utf-8')
        return access_key
    
    @staticmethod
    def create_access_key_for_user(user_email):
        """
        Create and store a new access key for a user to access their documents.
        The key is stored in reversed order (right-to-left) in the database for security.
        
        Args:
            user_email (str): Email of the user.
        
        Returns:
            str: The generated access key (original, not reversed).
        """
        try:
            # Generate new access key
            access_key = DocumentModel.generate_access_key()
            
            # Store the access key REVERSED (droite-vers-gauche) in the database
            # The last character becomes the first, etc.
            reversed_key = access_key[::-1]
            
            # Store the access key with expiration (valid for current session)
            key_record = {
                "user_email": user_email,
                "access_key": reversed_key,  # Stored in reversed order
                "created_at": datetime.now(),
                "is_used": False,
                "expires_at": datetime.now()  # Will be updated with expiration logic
            }
            
            # Remove any previous unused keys for this user
            DocumentModel.access_keys_collection.delete_many({
                "user_email": user_email,
                "is_used": False
            })
            
            # Insert new key (stored reversed)
            DocumentModel.access_keys_collection.insert_one(key_record)
            
            # Return the ORIGINAL key (not reversed) - this is what the user receives
            return access_key
        except Exception as e:
            print(f"Error creating access key: {str(e)}")
            return None
    
    @staticmethod
    def verify_access_key(user_email, access_key):
        """
        Verify if the provided access key is valid for the user.
        The key in the database is stored reversed (right-to-left),
        so we need to reverse the provided key to compare.
        
        Args:
            user_email (str): Email of the user.
            access_key (str): The access key to verify (original format from user).
        
        Returns:
            bool: True if the key is valid, False otherwise.
        """
        try:
            # Reverse the provided key to match the stored format (droite-vers-gauche)
            reversed_key = access_key[::-1]
            
            key_record = DocumentModel.access_keys_collection.find_one({
                "user_email": user_email,
                "access_key": reversed_key,  # Compare with reversed key
                "is_used": False
            })
            
            if key_record:
                # Mark the key as used
                DocumentModel.access_keys_collection.update_one(
                    {"_id": key_record["_id"]},
                    {"$set": {"is_used": True, "used_at": datetime.now()}}
                )
                return True
            return False
        except Exception as e:
            print(f"Error verifying access key: {str(e)}")
            return False
    
    @staticmethod
    def upload_document(user_email, filename, file_content, file_type, description=""):
        """
        Upload a document for a user.
        
        Args:
            user_email (str): Email of the document owner.
            filename (str): Name of the file.
            file_content (bytes): Binary content of the file.
            file_type (str): MIME type of the file.
            description (str): Optional description of the document.
        
        Returns:
            tuple: (success: bool, message: str, document_id: str or None)
        """
        try:
            # Encode file content to base64 for storage
            encoded_content = base64.b64encode(file_content).decode('utf-8')
            
            document = {
                "user_email": user_email,
                "filename": filename,
                "file_content": encoded_content,
                "file_type": file_type,
                "description": description,
                "uploaded_at": datetime.now(),
                "updated_at": datetime.now(),
                "file_size": len(file_content)
            }
            
            result = DocumentModel.collection.insert_one(document)
            return True, "Document uploaded successfully.", str(result.inserted_id)
        except Exception as e:
            print(f"Error uploading document: {str(e)}")
            return False, f"Error uploading document: {str(e)}", None
    
    @staticmethod
    def get_user_documents(user_email):
        """
        Get all documents for a specific user.
        
        Args:
            user_email (str): Email of the user.
        
        Returns:
            list: List of documents (without file content for efficiency).
        """
        try:
            documents = list(DocumentModel.collection.find(
                {"user_email": user_email},
                {"file_content": 0}  # Exclude file content for listing
            ).sort("uploaded_at", -1))
            
            # Convert ObjectId to string
            for doc in documents:
                doc["_id"] = str(doc["_id"])
            
            return documents
        except Exception as e:
            print(f"Error getting user documents: {str(e)}")
            return []
    
    @staticmethod
    def get_document_by_id(document_id, user_email):
        """
        Get a specific document by ID, ensuring the user owns it.
        
        Args:
            document_id (str): ID of the document.
            user_email (str): Email of the user (for ownership check).
        
        Returns:
            dict or None: The document if found and owned by user, None otherwise.
        """
        try:
            document = DocumentModel.collection.find_one({
                "_id": ObjectId(document_id),
                "user_email": user_email
            })
            
            if document:
                document["_id"] = str(document["_id"])
                # Decode file content
                if "file_content" in document:
                    document["file_content_decoded"] = base64.b64decode(document["file_content"])
            
            return document
        except Exception as e:
            print(f"Error getting document: {str(e)}")
            return None
    
    @staticmethod
    def delete_document(document_id, user_email):
        """
        Delete a document by ID, ensuring the user owns it.
        
        Args:
            document_id (str): ID of the document.
            user_email (str): Email of the user (for ownership check).
        
        Returns:
            tuple: (success: bool, message: str)
        """
        try:
            result = DocumentModel.collection.delete_one({
                "_id": ObjectId(document_id),
                "user_email": user_email
            })
            
            if result.deleted_count > 0:
                return True, "Document deleted successfully."
            return False, "Document not found or you don't have permission to delete it."
        except Exception as e:
            print(f"Error deleting document: {str(e)}")
            return False, f"Error deleting document: {str(e)}"
    
    @staticmethod
    def update_document_description(document_id, user_email, new_description):
        """
        Update the description of a document.
        
        Args:
            document_id (str): ID of the document.
            user_email (str): Email of the user (for ownership check).
            new_description (str): New description for the document.
        
        Returns:
            tuple: (success: bool, message: str)
        """
        try:
            result = DocumentModel.collection.update_one(
                {"_id": ObjectId(document_id), "user_email": user_email},
                {"$set": {"description": new_description, "updated_at": datetime.now()}}
            )
            
            if result.modified_count > 0:
                return True, "Document description updated successfully."
            return False, "Document not found or you don't have permission to update it."
        except Exception as e:
            print(f"Error updating document: {str(e)}")
            return False, f"Error updating document: {str(e)}"
