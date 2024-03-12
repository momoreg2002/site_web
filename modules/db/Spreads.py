from .MongoDBAtlasConnexion import MongoDBAtlasConnexion

class Spreads:
    def __init__(self, db_name='ICE', collection_name='SPREADS'):
        # Établissement de la connexion lors de l'initialisation de l'instance
        self.db_name = db_name
        self.collection_name = collection_name
        self.db_connection = MongoDBAtlasConnexion(self.db_name, self.collection_name)
        self.db_connection.connect()  # Établit la connexion et stocke la collection
        self.collection = self.db_connection.collection

    def insert_spread(self, data : dict):
        """Insère un nouveau document dans la collection SPREADS."""
        result = self.collection.insert_one(data)
        return result.inserted_id 

    def find_spread_by_currency(self, currency_code :str):
        """Trouve un document par son code de devise."""
        return self.collection.find_one({"Currency_Code": currency_code})

    def update_spread(self, currency_code : str, buy_p : float, sell_p : float):
        """Met à jour le spread pour une devise spécifique."""
        result = self.collection.update_one(
            {"Currency_Code": currency_code},
            {"$set": {"Buy_P": buy_p, "Sell_P": sell_p}}
        )
        return result
    
    def delete_all_rates(self):
        """Supprime tous les documents de la collection RATES."""
        result = self.collection.delete_many({})
        return result.deleted_count

    def delete_spread(self, currency_code :str):
        """Supprime un document par son code de devise."""
        result = self.collection.delete_one({"Currency_Code": currency_code})
        return result.deleted_count

    def get_all_spreads(self) -> list:
        rates_cursor = self.collection.find({})
        return list(rates_cursor)
    
    def check_update_insert_spread(self, currency_code, p_buy, p_sell):
        # Vérifie si la devise existe déjà
        if self.collection.find_one({"Currency_Code": currency_code}):
            # Mise à jour si elle existe
            result = self.collection.update_one(
                {"Currency_Code": currency_code},
                {"$set": {"Buy_P": p_buy, "Sell_P": p_sell}}
            )
            return result.modified_count > 0  # Retourne True si au moins un document est mis à jour
        else:
            # Insertion si elle n'existe pas
            result = self.collection.insert_one({
                "Currency_Code": currency_code,
                "Buy_P": p_buy,
                "Sell_P": p_sell
            })
            return result.inserted_id is not None  
    
    def close_connection(self):
        """Ferme explicitement la connexion MongoDB."""
        if self.db_connection:
            self.db_connection.close_connection()
