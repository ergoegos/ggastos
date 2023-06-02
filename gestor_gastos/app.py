from collections import namedtuple
import yaml
from yaml.loader import SafeLoader
import pandas as pd
import streamlit as st
import streamlit as st
import streamlit_authenticator as stauth
from services.database import Database
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.errors import HttpError
from google.oauth2.credentials import Credentials
from services.data_handler import get_data
import json
from views.figures import Figures
from streamlit_option_menu import option_menu


st.set_page_config(layout="wide", initial_sidebar_state="collapsed")


st.write("""
<style>
div[data-testid="metric-container"] {
    background-color: #F5F5F5;
    border: 1px solid black;
   padding: 5% 5% 5% 10%;
   border-radius: 5px;
   color: black;
   overflow-wrap: break-word;
}

/* breakline for metric text         */
div[data-testid="metric-container"] > label[data-testid="stMetricLabel"] > div {
   overflow-wrap: break-word;
   white-space: break-spaces;
   color: black;
}
</style>
""", unsafe_allow_html=True)


SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']

with open('./gestor_gastos/config.yaml') as file:
    config = yaml.load(file, Loader=SafeLoader)


with Database() as db:
    credentials_database = db.get_credentials()
    config["credentials"] = credentials_database

authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days'],
    config['preauthorized']
)


if "register" not in st.session_state:
    if "sheet" in st.session_state:
        with st.form("my_form"):
            st.write("Introduzca el ID de su hoja de cálculo. Utilice la siguiente plantilla: https://docs.google.com/spreadsheets/d/1u0otFPqUlrQZLQsOyxuEngewC2-7PsUTf6kTERMZOKA/edit#gid=886764515. En este ejemplo, el ID es '1u0otFPqUlrQZLQsOyxuEngewC2-7PsUTf6kTERMZOKA'")
            sheet_id = st.text_input("Sheet_ID")
            submitted = st.form_submit_button("Submit"
                                              )
            if submitted:
                with Database() as db:
                    db.insert_sheet_id(st.session_state["sheet"], sheet_id)
                    flow = InstalledAppFlow.from_client_secrets_file(
                            './gestor_gastos/credentials.json', SCOPES)
                    credentials = flow.run_local_server(port=0)
                    db.update_credentials(st.session_state["sheet"], credentials.to_json())
                    del st.session_state["sheet"]

                st.experimental_rerun()
    else:

        name, authentication_status, username = authenticator.login(
            'Login', 'main')
        if st.session_state["authentication_status"] is None:
            boton = st.button("Register")
            if boton:
                st.session_state["register"] = True
                st.experimental_rerun()

        if authentication_status:
        
            if "credentials" not in st.session_state:
                with Database() as db:
                    credentials, sheet = db.check_credentials(username)
                
                    if credentials is None:
                        print("No se han encontrado las credentials del usuario")
                        flow = InstalledAppFlow.from_client_secrets_file(
                            './gestor_gastos/credentials.json', SCOPES)
                        credentials = flow.run_local_server(bind_addr="192.168.1.139")
                        db.update_credentials(username, credentials.to_json())
                    else:
                        credentials = Credentials.from_authorized_user_info(
                            json.loads(credentials), SCOPES)
                        if not credentials.valid:
                            if credentials.expired and credentials.refresh_token:
                                print("credentials expired, refreshing ...")
                                credentials.refresh(Request())
                                db.update_credentials(
                                    username, credentials.to_json())

                    service = build('sheets', 'v4', credentials=credentials)
                    with st.spinner('Descargando datos ...'):
                        get_data(username, service, sheet)
                        st.session_state["credentials"] = True
                        st.experimental_rerun()

            else:

                col1, col2 = st.columns((15, 1))
                with col1:
                    selected = option_menu(None, ["Gastos", "Ingresos", "Finanzas", 'Sync'],
                                        icons=[None, None, None, 'gear'],
                                        menu_icon="", default_index=0, orientation="horizontal",
                                        styles={
                        "container": {"padding": "0!important", "background-color": "#F5F5F5", "border": "1px solid black"},
                        "icon": {"color": "#F5F5F5", "font-size": "0px"},
                        "nav-link": {"font-size": "25px", "text-align": "center", "margin": "0px", "--hover-color": "#eee"},
                        "nav-link-selected": {"background-color": "grey"},
                    })
                with col2:
                     authenticator.logout('Logout', 'main')


                figures = Figures(username)

                if selected == "Gastos":

                    col1, col2, col3 = st.columns(3)

                    col1.metric(**figures.last_month_metric("expenses"))
                    col2.metric(**figures.max_source("expenses"))
                    col3.metric(**figures.vs_projection_metric("expenses"))

                    col1, col2 = st.columns(2)

                    with col1:
                        with st.expander(expanded=True, label=""):
                            st.plotly_chart(
                                figures.m_exp_total_evolution_line())
                    with col2:
                        with st.expander(expanded=True, label=""):
                            st.plotly_chart(
                                figures.m_exp_by_concept_total_evolution_bar())

                    col1, col2 = st.columns((3, 7))

                    with col1:
                        with st.expander(expanded=True, label=""):
                            st.plotly_chart(
                                figures.m_percent_current_pie("expenses"))
                    with col2:
                        with st.expander(expanded=True, label=""):
                            st.plotly_chart(
                                figures.m_percent_evolution_pm_bar_by_concept("expenses"))
                    with st.expander(expanded=True, label=""):
                        st.plotly_chart(
                            figures.m_vs_projection_evolution_line("expenses"))

                if selected == "Ingresos":

                    col1, col2, col3 = st.columns(3)
                    col1.metric(**figures.last_month_metric("incomes"))
                    col2.metric(**figures.max_source("expenses"))
                    col3.metric(**figures.vs_projection_metric("incomes"))

                    col1, col2 = st.columns(2)
                    with col1:
                        with st.expander(expanded=True, label=""):
                            st.plotly_chart(
                                figures.m_inc_total_evolution_line())
                    with col2:
                        with st.expander(expanded=True, label=""):
                            st.plotly_chart(
                                figures.m_inc_by_concept_total_evolution_bar())

                    col1, col2 = st.columns((3, 7))

                    with col1:
                        with st.expander(expanded=True, label=""):
                            st.plotly_chart(
                                figures.m_percent_current_pie("incomes"))
                    with col2:
                        with st.expander(expanded=True, label=""):
                            st.plotly_chart(
                                figures.m_percent_evolution_pm_bar_by_concept("incomes"))
                    with st.expander(expanded=True, label=""):
                        st.plotly_chart(
                            figures.m_vs_projection_evolution_line("incomes"))

                if selected == "Finanzas":
                    with st.expander(expanded=True, label=""):
                        st.plotly_chart(figures.savings_evolution_line())
                    col1, col2 = st.columns((4, 6))

                    with col1:
                        with st.expander(expanded=True, label=""):
                            st.plotly_chart(
                                figures.progress_saving_projection())
                    with col2:
                        with st.expander(expanded=True, label=""):
                            st.plotly_chart(figures.expense_vs_income())

                if selected == "Sync":

                    with st.spinner('Descargando datos ...'):
                        with Database() as db:
                            credentials, sheet = db.check_credentials(username)
                            credentials = Credentials.from_authorized_user_info(
                                json.loads(credentials), SCOPES)
                        service = build(
                            'sheets', 'v4', credentials=credentials)

                        get_data(username, service, sheet)



        elif authentication_status is False:
            st.error('Username/password is incorrect')
        elif authentication_status is None:
            st.warning('Please enter your username and password')


else:
    if authenticator.register_user('Register user', preauthorization=False):
        with Database() as db:
            users_database = set(
                list(db.get_credentials()["usernames"].keys()))
            new_users = set(list(config["credentials"]["usernames"].keys()))
            new_user = new_users - users_database
            for user in new_user:
                db.insert_user(user, config["credentials"]["usernames"][user])
            del st.session_state["register"]
            st.session_state["sheet"] = user
            st.experimental_rerun()
