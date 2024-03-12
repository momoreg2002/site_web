import streamlit as st
import pandas as pd

from modules.views import menu, hide_footer, login
from modules.data_processing import data_insert_file, data_insert_manuel ,data_insert_correction, data_visualization, data_insert_spread, rates_calculation, users_management

def main():
    hide_footer()
    if not st.session_state.get("users") :
        login()
    else:
        st.sidebar.title("Bienvenue " + st.session_state.get("users")['Prenom'])
        image_path = './static/image/OIP.jpg' 
        st.sidebar.image(image_path)
        choix = menu(options=["Spot", "Spreads", "Rates", 'Users'],
                     icons=['graph-up-arrow', 'bar-chart-line', 'currency-exchange', 'people'] ,
                     orientation="vertical")
        
        match choix:
            case 0:
                st.markdown('''<p style="font-size:35px;">MARKET RATES </p>''', unsafe_allow_html=True)
               
                option = st.radio("Choisir une option :", 
                                  ("Insérer le fichier", "Insérer une devise manuellement", "Corriger une valeur", "Visualiser les données"),
                                  key='option')


                if option == "Insérer le fichier":
                    data_insert_file()
                    
                elif option == "Insérer une devise manuellement":
                    data_insert_manuel()
                    
                elif option == "Corriger une valeur":
                    data_insert_correction()

                elif option == "Visualiser les données":
                    data_visualization()

 
            case 1:
                data_insert_spread()

            case 2:
                rates_calculation()

            case 3:
                users_management()


if __name__ == '__main__':
    main()
