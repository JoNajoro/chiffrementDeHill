from pymongo import MongoClient
from config.config import Config

# Initialisation du client MongoDB
client = MongoClient(Config.MONGO_URI)

# Accès à la base "dren_db"
db = client.get_database("dren_db")

def test_connection():
    try:
        # Liste les collections pour vérifier la connexion
        collections = db.list_collection_names()
        print("✅ Connexion à MongoDB réussie ! Collections existantes :", collections)
    except Exception as e:
        print("❌ Erreur de connexion à MongoDB :", e)
