from .MongoDBAtlasConnexion import MongoDBAtlasConnexion

class Rate:
    def __init__(self, db_name='ICE', collection_name='RATES'):
        # Établissement de la connexion lors de l'initialisation de l'instance
        self.db_name = db_name
        self.collection_name = collection_name
        self.db_connection = MongoDBAtlasConnexion(self.db_name, self.collection_name)
        self.db_connection.connect()  # Établit la connexion et stocke la collection
        self.collection = self.db_connection.collection

    def insert_rate(self, data : dict):
        """Insère un nouveau taux dans la collection."""
        result = self.collection.insert_one(data)
        return result.inserted_id
    
    def insert_many_rates(self, rates_list : list) -> list:
        """Insère plusieurs documents de taux dans la collection.
        
        Args:
            rates_list (list): Une liste de dictionnaires, où chaque dictionnaire représente un taux à insérer.
        
        Returns:
            list: Les identifiants des documents insérés.
        """
        if not rates_list or not isinstance(rates_list, list):
            raise ValueError("rates_list doit être une liste de dictionnaires.")
        
        result = self.collection.insert_many(rates_list)
        return result.inserted_ids


    def find_rate_by_currency(self, currency_code :str):
        """Trouve un taux par son code de devise."""
        return self.collection.find_one({"Currency_Code": currency_code})

    def update_rate(self, currency_code :str, buy_p :float, sell_p :float):
        """Met à jour le taux d'achat et de vente pour une devise donnée."""
        result = self.collection.update_one(
            {"Currency_Code": currency_code},
            {"$set": {"Buy_P": buy_p, "Sell_P": sell_p}}
        )
        return result.modified_count

    def delete_rate(self, currency_code :str):
        """Supprime un taux par son code de devise."""
        result = self.collection.delete_one({"Currency_Code": currency_code})
        return result.deleted_count

    def get_all_rates(self) -> list:
        """Récupère tous les taux de la collection."""
        rates_cursor = self.collection.find({})
        return list(rates_cursor)
    
    def delete_all_rates(self):
        """Supprime tous les documents de la collection RATES."""
        result = self.collection.delete_many({})
        return result.deleted_count

    
    def close_connection(self):
        """Ferme explicitement la connexion MongoDB."""
        if self.db_connection:
            self.db_connection.close_connection()


