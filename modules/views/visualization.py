
from streamlit_option_menu import option_menu
import streamlit as st
from ..db.Users import Users
import streamlit as st
from ..data_processing import is_valid_email


def menu(options: list, icons: list, orientation: str = 'vertical') -> int:
    """
    Affiche un menu d'options avec des icônes dans la sidebar de Streamlit en utilisant streamlit_option_menu.

    Args:
        options (list of str): Une liste contenant les labels des options du menu.
        icons (list of str): Une liste contenant les icônes correspondant aux options du menu.
        orientation (str): Orientation du menu ('horizontal' ou 'vertical'). Valeur par défaut : 'vertical'.

    Returns:
        int: L'index de l'option sélectionnée.
    """

    # Afficher le menu d'options et obtenir le label de l'option sélectionnée dans la sidebar
    with st.sidebar:
        selected_label = option_menu(None, options, icons=icons, orientation=orientation, key='menu', styles={"nav-link-selected": {"background-color": "blue"}})

    # Trouver l'index de l'option sélectionnée
    selected_index = options.index(selected_label)
    
    # Retourner l'index de l'option sélectionnée
    return selected_index


def hide_footer():
    hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            </style>
            """
    st.markdown(hide_streamlit_style, unsafe_allow_html=True) 

def login():
    st.image('./static/image/OIP.jpg')
    mail = st.text_input("Email", max_chars=50)
    mpass = st.text_input("Password", type='password')
    
    if st.button("Login"):
        if mail and mpass :
            if not is_valid_email(mail):
                st.error("L'adresse email n'est pas valide.")
                return
            
            users_manager = Users()
            try:
                if users_manager.verify_user(mail, mpass):
                    st.session_state['user_status'] = True
                    st.session_state['users'] = users_manager.find_user_by_email(mail)
                    st.experimental_rerun()
                else:
                    st.error("Mot de passe ou Email est incorrect.")
            finally:
                users_manager.close_connection()
        else:
            st.error("Veuillez entrer à la fois l'email et le mot de passe.")

