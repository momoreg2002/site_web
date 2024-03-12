import os
import pymongo 
import configparser


class MongoDBAtlasConnexion:
    def __init__(self, db_name, collection_name):
        self.uri = self._get_val_env()  # Lire le URI depuis la variable d'environnement
        if not self.uri:
            raise ValueError("La variable d'environnement MONGO_DB_URI n'est pas définie.")
        self.db_name = db_name
        self.collection_name = collection_name
        self.client = None
        self.db = None
        self.collection = None

    def connect(self):
        """Établit une connexion à MongoDB Atlas et sélectionne la base de données et la collection."""
        try:
            self.client = pymongo.MongoClient(self.uri)
            self.db = self.client[self.db_name]
            self._ensure_collection_exists()
            print(f"Connecté à MongoDB Atlas, base de données '{self.db_name}', collection '{self.collection_name}'.")
        except Exception as e:
            print(f"Erreur lors de la connexion à MongoDB Atlas: {e}")

    def _ensure_collection_exists(self):
        """Vérifie si la collection existe et la crée si ce n'est pas le cas."""
        if self.collection_name not in self.db.list_collection_names():
            self.db.create_collection(self.collection_name)
            print(f"La collection '{self.collection_name}' a été créée.")
        else:
            print(f"La collection '{self.collection_name}' existe déjà.")
        self.collection = self.db[self.collection_name]

    def close_connection(self):
        """Ferme la connexion au client MongoDB."""
        if self.client:
            self.client.close()
            print("Connexion à MongoDB Atlas fermée.")

    def _get_val_env(self):
        config = configparser.ConfigParser()
        config.read(os.path.join(os.path.dirname(__file__), '../../config/config.ini'))
        uri = config['MongoAtlas']['MONGO_DB_URI']
        return uri


