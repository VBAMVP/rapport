# -*- coding: utf-8 -*-

import json
import streamlit as st
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import os

# Fonctions pour les opérations Google Docs et Drive
def authenticate_google():
    """Authenticate with Google and return service objects for Docs and Drive."""
    auth.authenticate_user()
    creds, _ = default(scopes=['https://www.googleapis.com/auth/drive',
                           'https://www.googleapis.com/auth/documents'])
    drive_service = build('drive', 'v3', credentials=creds)
    docs_service = build('docs', 'v1', credentials=creds)

def authenticate_google(creds_json):
    """Authenticate with Google using the provided JSON credentials."""
    scopes = ['https://www.googleapis.com/auth/drive', 'https://www.googleapis.com/auth/documents']

    flow = InstalledAppFlow.from_client_config(creds_json, scopes)
    flow.redirect_uri = ''  # Remplacez par votre URI de redirection réel

    if 'creds' not in st.session_state or not st.session_state['creds'].valid:
        if 'creds' in st.session_state and st.session_state['creds'].expired and st.session_state['creds'].refresh_token:
            st.session_state['creds'].refresh(Request())
        else:
            auth_url, _ = flow.authorization_url(prompt='consent')
            st.write('Veuillez vous connecter à Google:', auth_url)
            code = st.text_input('Entrez le code de Google ici:')
            if code:
                flow.fetch_token(code=code)
                st.session_state['creds'] = flow.credentials

    return st.session_state.get('creds', None)

# Streamlit Interface
st.title('Google Docs Creator')

# Téléchargez le fichier client_secret.json
uploaded_file = st.file_uploader("Upload client_secret.json", type="json")
if uploaded_file is not None:
    # Charger les données du fichier JSON
    creds_json = json.load(uploaded_file)

    # Appel de la fonction d'authentification avec les données JSON
    creds = authenticate_google(creds_json)
    if creds:
        # Création des services Google Docs et Drive
        drive_service = build('drive', 'v3', credentials=creds)
        docs_service = build('docs', 'v1', credentials=creds)
