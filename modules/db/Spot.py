from .MongoDBAtlasConnexion import MongoDBAtlasConnexion

class Spot:
    def __init__(self, db_name='ICE', collection_name='SPOT'):
        # Établissement de la connexion lors de l'initialisation de l'instance
        self.db_name = db_name
        self.collection_name = collection_name
        self.db_connection = MongoDBAtlasConnexion(self.db_name, self.collection_name)
        self.db_connection.connect()  # Établit la connexion et stocke la collection
        self.collection = self.db_connection.collection

    def round_rate(self, rate):
        """
        Arrondit le taux à six chiffres après la virgule, en utilisant le septième chiffre pour décider.
        """
        scale = 10**7
        temp = rate * scale
        seventh_digit = int(temp) % 10
        if seventh_digit > 5:
            return round(rate + 5 * 10**-7, 6)
        elif seventh_digit < 5:
            return round(rate, 6)
        else:  # seventh_digit == 5
            return round(rate + 5 * 10**-7, 6)

    def insert_spot(self, data: dict):
        """Insère un nouveau document dans la collection SPOT."""
        if 'Rate' in data:
            data['Rate'] = self.round_rate(data['Rate'])
        result = self.collection.insert_one(data)
        return result.inserted_id
    
    def insert_many_spot(self, rates_list: list) -> list:
        """Insère plusieurs documents de taux dans la collection."""
        for rate_data in rates_list:
            if 'Rate' in rate_data:
                rate_data['Rate'] = self.round_rate(rate_data['Rate'])
        result = self.collection.insert_many(rates_list)
        return result.inserted_ids

    def update_spot_rate(self, currency_code: str, new_rate: float, date: str):
        """Met à jour le taux pour une devise spécifique."""
        rounded_rate = self.round_rate(new_rate)
        result = self.collection.update_one(
            {"Currency_Code": currency_code},
            {"$set": {"Rate": rounded_rate, "UpdateDate": date}}
        )
        return result
 '''
    def insert_spot(self, data : dict):
        """Insère un nouveau document dans la collection SPOT."""
        result = self.collection.insert_one(data)
        return result.inserted_id
    
     def insert_many_spot(self, rates_list : list) -> list:
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
         '''

    def find_spot_by_currency(self, currency_code :str):
        """Trouve un document par son code de devise."""
        return self.collection.find_one({"Currency_Code": currency_code})

    '''def update_spot_rate(self, currency_code :str, new_rate : float, date :str):
        """Met à jour le taux pour une devise spécifique."""
        result = self.collection.update_one(
            {"Currency_Code": currency_code},
            {"$set": {"Rate": new_rate, "UpdateDate": date }}
        )
        return result
        
        '''

    def delete_spot(self, currency_code : str):
        """Supprime un document par son code de devise."""
        result = self.collection.delete_one({"Currency_Code": currency_code})
        return result.deleted_count
    
    def get_all_spot(self) -> list:
        rates_cursor = self.collection.find({})
        return list(rates_cursor)
    
    def delete_all_spot(self):
        """Supprime tous les documents de la collection RATES."""
        result = self.collection.delete_many({})
        return result.deleted_count
    
    def close_connection(self):
        """Ferme explicitement la connexion MongoDB."""
        if self.db_connection:
            self.db_connection.close_connection()
    
