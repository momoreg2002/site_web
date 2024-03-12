from .MongoDBAtlasConnexion import MongoDBAtlasConnexion
import hashlib

class Users:
    def __init__(self, db_name='ICE', collection_name='USERS'):
        # Établissement de la connexion lors de l'initialisation de l'instance
        self.db_name = db_name
        self.collection_name = collection_name
        self.db_connection = MongoDBAtlasConnexion(self.db_name, self.collection_name)
        self.db_connection.connect()  # Établit la connexion et stocke la collection
        self.collection = self.db_connection.collection
    
    def insert_user(self, user_data: dict):
        if not isinstance(user_data, dict):
            raise ValueError("user_data doit être un dictionnaire.")
        # Hachage du mot de passe avant insertion
        if 'Pwd' in user_data:
            user_data['Pwd'] = self.hash_password(user_data['Pwd'])
        result = self.collection.insert_one(user_data)
        return result.inserted_id
    
    def find_user_by_email(self, email: str) -> dict:
        """Trouve un utilisateur par son email."""
        return self.collection.find_one({"Email": email})

    def update_user(self, email: str, update_data: dict):
        """Met à jour un utilisateur spécifié par son email."""
        if not isinstance(update_data, dict):
            raise ValueError("update_data doit être un dictionnaire.")
        
        # Check if 'Pwd' is in update_data and hash it if present
        if 'Pwd' in update_data:
            update_data['Pwd'] = self.hash_password(update_data['Pwd'])

        result = self.collection.update_one(
            {"Email": email},
            {"$set": update_data}
        )
        return result.modified_count


    def delete_user(self, email: str):
        """Supprime un utilisateur spécifié par son email."""
        result = self.collection.delete_one({"Email": email})
        return result.deleted_count

    def get_all_users(self):
        """Récupère tous les utilisateurs de la collection USERS."""
        users_cursor = self.collection.find({})
        return list(users_cursor)
    
    def delete_all_users(self):
        """Supprime tous les documents de la collection USERS."""
        result = self.collection.delete_many({})
        return result.deleted_count
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Hashes the password using SHA256."""
        hashed_password = hashlib.sha256(password.encode('utf-8')).hexdigest()
        return hashed_password

    def verify_user(self, email: str, password: str) -> bool:
        """Verifies if the provided password for the user matches the stored hash."""
        user = self.collection.find_one({"Email": email})
        if user and 'Pwd' in user:
            hashed_input_password = Users.hash_password(password)  # Hash input password
            if hashed_input_password == user['Pwd']:  # Compare hashed passwords
                return True
        return False

 
 
    def close_connection(self):
        """Ferme explicitement la connexion MongoDB."""
        if self.db_connection:
            self.db_connection.close_connection()