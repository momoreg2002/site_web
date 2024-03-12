import pandas as pd
import re
from .db.Spot import Spot
from .db.Spreads import Spreads
from .db.Rates import Rate
from .db.Users import Users
import streamlit as st
from datetime import datetime
import pytz
import hashlib


def currency_needed():
    Currency_Code = ['USD', 'EUR', 'MXN', 'GBP', 'JPY', 'CHF', 'DOP', 'COP', 'MAD', 'CRC', 'THB', 'BRL', 'VND', 'IND']
    return Currency_Code

def load_data_txt_for_spot(file_obj):
    """
    Lire les données à partir de l'objet fichier téléchargé, filtrer selon les devises nécessaires,
    et les préparer pour l'insertion.
    
    Args:
        file_obj (UploadedFile): L'objet fichier téléchargé via st.file_uploader.
    
    Returns:
        list: Une liste de dictionnaires prêts à être insérés.
    """
    # Obtenir la liste des devises nécessaires
    needed_currencies = currency_needed()
    
    # Lire le contenu texte du fichier téléchargé
    content_text = file_obj.getvalue().decode("utf-8")
    
    lines = content_text.split('\n')
    data = []
    for line in lines:
        values = line.split('|')
        if len(values) >= 4 and values[1] in needed_currencies:
            try:
                spot_document = {
                    "Currency_Code": values[1],
                    "Rate": float(values[2]),
                    "UpdateDate": pd.to_datetime(values[3], errors='coerce').strftime('%Y-%m-%d') if pd.to_datetime(values[3], errors='coerce') is not pd.NaT else None
                }
                data.append(spot_document)
            except ValueError as e:
                # Gérer l'erreur de conversion (facultatif)
                print(f"Erreur lors de la conversion de la ligne: {line}. Erreur: {e}")
    return data

def canadien_date():
    timezone = pytz.timezone('America/Toronto')
    current_date_in_canada = datetime.now(timezone).date()
    formatted_date = current_date_in_canada.strftime('%Y-%m-%d')
    return formatted_date

def is_valid_email(email):
    """Valide l'adresse email avec une expression régulière simple."""
    if re.match(r"[^@]+@[^@]+\.[^@]+", email):
        return True
    else:
        return False
    

def data_insert_file():
    uploaded_file = st.file_uploader('Télécharger votre fichier TXT', type=['txt'])
    if uploaded_file is not None:
        with st.spinner("Traitement en cours..."):
            # Supposons que load_data_txt_for_spot a été ajustée pour traiter l'objet fichier
            data = load_data_txt_for_spot(uploaded_file)
            spot_manager = Spot()
            nb_delete = spot_manager.delete_all_spot()
            inserted_ids = spot_manager.insert_many_spot(data)
            if inserted_ids.count != 0:
                st.success("document inséré.")
            else:
                st.error("Aucun document inséré.")
            spot = spot_manager.get_all_spot()
            spot_manager.close_connection()
            if data is not None:
                df = pd.DataFrame(spot)
                df.drop('_id', axis=1, inplace=True)
                st.write(df) 
    

def data_insert_manuel():
    st.warning("Le code de devise doit être composé des deux premières lettres qui référent au nom du pays, suivies d'une lettre représentant la devise.")
    currencyCode = st.text_input("Entrez le code de devise (Exemple : USD pour le dollar américain)", "")
    rate = st.text_input("Entrez le taux de change", "")
    
    # Bouton de soumission
    submit_button = st.button('Soumettre')

    if submit_button:
        try: 
            currencyCode = currencyCode.upper()
            if currencyCode and len(currencyCode) == 3:
                spot_manager = Spot()
                currency = spot_manager.find_spot_by_currency(currencyCode)
                
                if currency:
                    st.error("Cette devise existe déjà dans la base de données.")
                    st.write("Voici les détails :")
                    df = pd.DataFrame([currency])
                    df.drop('_id', axis=1, inplace=True)
                    st.write(df)
                else:
                    rate = float(rate)  
                    formatted_date = canadien_date()

                    data = {
                        "Currency_Code": currencyCode,
                        "Rate": rate,
                        "UpdateDate": str(formatted_date)
                    }
                    
                    spot_manager.insert_spot(data)
                    st.success("Devise ajoutée avec succès.")
            else:
                st.error("Le code de devise doit avoir exactement 3 caractères.")
                
        except ValueError:
            st.error("Veuillez entrer un taux de change valide.")
        finally:
            if 'spot_manager' in locals():
                spot_manager.close_connection()


    

def data_insert_correction():
    spot_manager = Spot()
    currency_list = spot_manager.get_all_spot()
    currency_code_list = [currency['Currency_Code'] for currency in currency_list]  # Assurez-vous que 'Currency_Code' est la clé correcte

    option = st.selectbox(
        'Choisissez la devise à mettre à jour :',
        currency_code_list)

    new_rate = st.text_input('Entrez le nouveau taux d\'échange :', '')

    if st.button('Mettre à jour'):
        try:
            new_rate = float(new_rate)  
            formatted_date = canadien_date()
            # Mettre à jour le taux d'échange dans la base de données
            update_result = spot_manager.update_spot_rate(option, new_rate, formatted_date)
            
            if update_result.modified_count > 0:
                st.success(f"Le taux d'échange de la devise {option} a été mis à jour avec succès.")
            else:
                st.warning(f"Aucune mise à jour n'a été effectuée. Vérifiez si le taux d'échange est différent du précédent.")
        except ValueError:
            st.error("Veuillez entrer un taux d'échange valide.")
        finally:
            if 'spot_manager' in locals():
                spot_manager.close_connection()


def data_visualization():
    st.write("Spot :")
    spot_manager = Spot()
    data = spot_manager.get_all_spot()
    df = pd.DataFrame(data)
    df.drop('_id', axis=1, inplace=True)
    st.write(df)
    spot_manager.close_connection()


def data_insert_spread():
    spot_manager = Spot()  # Assurez-vous que Spot est correctement importé/initié

    # Obtention de la liste des devises
    currency_list = spot_manager.get_all_spot()
    currency_code_list = [currency['Currency_Code'] for currency in currency_list]

    # Interface utilisateur pour insérer les spreads
    st.title("Insérer les marges d'une devise")
    option = st.selectbox('Choisissez la devise à mettre à jour :', currency_code_list)
    p_buy = st.text_input("Entrez le pourcentage de Buy", "")
    p_sell = st.text_input("Entrez le pourcentage de Sell", "")
    
    # Bouton de soumission
    submit_button = st.button('Soumettre')
    
    if submit_button:
        # Validation initiale des pourcentages avant de procéder
        error_flag = False  # Drapeau pour signaler une erreur de validation
        try:
            p_buy = float(p_buy)
            p_sell = float(p_sell)
            if p_buy < 0 or p_sell < 0:
                st.error("Les pourcentages ne peuvent pas être négatifs.")
                error_flag = True
        except ValueError:
            st.error("Veuillez entrer des valeurs numériques valides pour les pourcentages.")
            error_flag = True

        if not error_flag:
            # Connexion à la base de données seulement si les validations sont passées
            spreads_manager = Spreads()
            try:
                
                # Insérer les données dans la base de données
                update_result = spreads_manager.check_update_insert_spread(option,p_buy,p_sell)
                
                if update_result:
                    st.success(f"Les marges d'échange de la devise {option} ont été mises à jour avec succès.")
                else:
                    st.warning("Aucune mise à jour n'a été effectuée. Vérifiez si le taux d'échange est différent du précédent.")
            finally:
                # Fermeture de la connexion
                spreads_manager.close_connection()
            
            # Fermeture de la connexion de spot_manager
            spot_manager.close_connection()

    visualization_button = st.button('Visualiser les marges :bar_chart:')
    
    if visualization_button:
        spreads_manager = Spreads()
        data = spreads_manager.get_all_spreads()
        df = pd.DataFrame(data)
        df.drop('_id', axis=1, inplace=True)
        st.write(df)
        spreads_manager.close_connection()


def rates_calculation():
    col1, col2 = st.columns(2)

    with col1:
        st.title("Visualiser les taux:")
        visualization_button = st.button('Visualiser les taux finaux', key='visualize')
        
        if visualization_button:
            rates_manager = Rate()
            try:
                data = rates_manager.get_all_rates()
                df = pd.DataFrame(data)
                if '_id' in df.columns:  # S'assurer que la colonne '_id' existe avant de la supprimer
                    df.drop('_id', axis=1, inplace=True)
                st.dataframe(df)
            finally:
                rates_manager.close_connection()
    
    with col2:
        st.title("Générer les taux :")
        btn_calcul = st.button('Lancer le traitement', key='calculate')
        
        if btn_calcul:
            with st.spinner("Traitement en cours..."):
                # Création des instances et récupération des données
                spot_manager = Spot()
                spreads_manager = Spreads()

                try:
                    data_spot = spot_manager.get_all_spot()
                    df_spot = pd.DataFrame(data_spot)
                    data_spreads = spreads_manager.get_all_spreads()
                    df_spreads = pd.DataFrame(data_spreads)

                    # Identification des devises communes
                    common_currencies = set(df_spot['Currency_Code']).intersection(df_spreads['Currency_Code'])

                    # Préparation des taux à insérer
                    rates_to_insert = []
                    for currency in common_currencies:
                        spot_rate = df_spot.loc[df_spot['Currency_Code'] == currency, 'Rate'].iloc[0]
                        buy_margin = df_spreads.loc[df_spreads['Currency_Code'] == currency, 'Buy_P'].iloc[0] / 100
                        sell_margin = df_spreads.loc[df_spreads['Currency_Code'] == currency, 'Sell_P'].iloc[0] / 100
                        final_rate_buy = spot_rate * (1 + buy_margin )
                        final_rate_sell = spot_rate * (1 - sell_margin )
                        rates_to_insert.append({'Currency_Code': currency, 'Rate_Buy': final_rate_buy, 'Rate_Sell': final_rate_sell})

                    # Insertion des nouveaux taux après suppression des anciens
                    rate_manager = Rate()
                    result = rate_manager.delete_all_rates()  # Assurez-vous que cette méthode retourne le nombre de lignes affectées
                    if result >= 0:  # Cela suppose que delete_rate retourne le nombre de taux supprimés, même si ce nombre est 0
                        rate_manager.insert_many_rates(rates_to_insert)

                    # Signalement des devises non communes
                    non_common_currencies = set(df_spot['Currency_Code']).symmetric_difference(df_spreads['Currency_Code'])
                    if non_common_currencies:
                        st.warning(f"Les devises suivantes ne sont pas communes entre Spot et Spreads, et ne seront pas traitées : {', '.join(non_common_currencies)}")

                    st.success("Taux générés et insérés avec succès.")
                finally:
                    # Assurez-vous de fermer les connexions dans un bloc finally pour garantir qu'elles se ferment correctement
                    spot_manager.close_connection()
                    spreads_manager.close_connection()


def users_management():
    users_manager = Users()

    st.title('Gestion des utilisateurs')

    # Affichage des utilisateurs
    users_list = users_manager.get_all_users()
    if users_list:
        # Assurez-vous que les noms des colonnes dans DataFrame correspondent à ceux dans votre base de données
        users_df = pd.DataFrame(users_list)
        users_df.drop('Pwd', axis=1, inplace=True)
        users_df.drop('_id', axis=1, inplace=True)
        st.dataframe(users_df)
    else:
        st.write("Aucun utilisateur disponible.")

    # Ajouter un utilisateur
    st.header('Ajouter un nouvel utilisateur')
    with st.form("add_user_form"):
        prenom = st.text_input('Prénom', max_chars=50)
        nom = st.text_input('Nom', max_chars=50)
        email = st.text_input('Email', max_chars=50)
        pwd = st.text_input('Mot de passe', type="password")
        
        submit_button = st.form_submit_button('Ajouter')

        if submit_button:
            # Vérifie si l'email existe déjà
            if users_manager.find_user_by_email(email):
                st.error('Email déjà utilisé.')
            else:
                # Appel à la méthode insert_user de votre classe Users pour ajouter l'utilisateur
                users_manager.insert_user({"Prenom": prenom, "Nom": nom, "Email": email, "Pwd": pwd})
                st.success(f'Utilisateur {prenom} {nom} ajouté avec succès.')

    # Sélectionner l'utilisateur à modifier ou à supprimer par email
    st.header("Modifier un utilisateur")
    with st.form("edit_user_form"):
        user_emails = [user['Email'] for user in users_manager.get_all_users()]
        selected_email = st.selectbox('Sélectionner l\'email de l\'utilisateur', options=user_emails)
        user_details = users_manager.find_user_by_email(selected_email)

        if user_details:
            prenom = st.text_input("Prénom", value=user_details.get('Prenom', ''))
            nom = st.text_input("Nom", value=user_details.get('Nom', ''))
            pwd = st.text_input("Nouveau mot de passe (laisser vide pour ne pas changer)", type="password")

            update_button = st.form_submit_button('Mettre à jour')
            if update_button:
                update_data = {"Prenom": prenom, "Nom": nom}
                if pwd:  # Si un nouveau mot de passe est fourni, incluez-le dans les données de mise à jour
                    update_data["Pwd"] = pwd
                users_manager.update_user(selected_email, update_data)
                st.success(f'Utilisateur {prenom} {nom} mis à jour avec succès.')

    # Gestion de la suppression d'un utilisateur
    st.header("Supprimer un utilisateur")
    delete_email = st.selectbox('Sélectionner l\'email de l\'utilisateur à supprimer', options=user_emails)
    supprimer = st.button('Supprimer')
    if supprimer:
        users_manager.delete_user(delete_email)
        st.success(f'Utilisateur {delete_email} supprimé avec succès.')