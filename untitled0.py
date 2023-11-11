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
    flow.redirect_uri = 'https://rapport-mytnctohgff55ttq3tgr8g.streamlit.app/'  # Remplacez par votre URI de redirection réel

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
def create_google_doc(title):
    """Create a Google Doc with the given title."""
    try:
        docs_service = build('docs', 'v1', credentials=creds)
    except Exception as e:
        print(e)  # Affiche l'erreur dans la console
        st.error(f"Une erreur est survenue : {e}")  # Affiche l'erreur dans l'interface Streamlit
    document = docs_service.documents().create(body={'title': title}).execute()
    return document.get('documentId')

def upload_image_to_drive(image_path):
    """Upload an image to Google Drive and return its ID."""
    drive_service = build('drive', 'v3', credentials=creds)
    file_metadata = {'name': os.path.basename(image_path), 'mimeType': 'image/png'}
    media = MediaFileUpload(image_path, mimetype='image/png')
    file = drive_service.files().create(body=file_metadata, media_body=media, fields='id').execute()
    return file.get('id')

def insert_image_to_doc(document_id, image_id):
    """Insert an image into a Google Doc."""
    docs_service = build('docs', 'v1', credentials=creds)
    requests = [{'insertInlineImage': {
                    'location': {'index': 1},
                    'uri': f'https://drive.google.com/uc?id={image_id}',
                    'objectSize': {'height': {'magnitude': 50, 'unit': 'PT'}, 'width': {'magnitude': 50, 'unit': 'PT'}}}}]
    docs_service.documents().batchUpdate(documentId=document_id, body={'requests': requests}).execute()

def insert_text_to_doc(document_id, text):
    """Insert text into a Google Doc."""
    docs_service = build('docs', 'v1', credentials=creds)
    end_index = 1 # You might want to find the correct end index where to insert the text
    requests = [{'insertText': {'location': {'index': end_index}, 'text': text}}]
    docs_service.documents().batchUpdate(documentId=document_id, body={'requests': requests}).execute()

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

# Formulaire pour créer un nouveau document
with st.form("create_doc"):
    doc_title = st.text_input("Enter the title for the new document")
    submitted1 = st.form_submit_button("Create Document")
    if submitted1:
        # Créer le document et afficher l'ID
        document_id = create_google_doc(doc_title)
        st.write(f"Document created with ID: {document_id}")

# Télécharger et insérer l'image
with st.form("upload_image"):
    image_file = st.file_uploader("Upload an image", type=['png', 'jpg', 'jpeg'])
    submitted2 = st.form_submit_button("Upload and Insert Image")
    if submitted2 and image_file:
        # Télécharger l'image sur Google Drive et l'insérer dans le document
        image_path = image_file.name
        with open(image_path, "wb") as f:
            f.write(image_file.getbuffer())
        image_id = upload_image_to_drive(image_path)
        insert_image_to_doc(document_id, image_id)
        st.write("Image inserted in the document.")

# Formulaire pour insérer du texte
with st.form("insert_text"):
    text = st.text_area("Enter text to insert into the document")
    submitted3 = st.form_submit_button("Insert Text")
    if submitted3:
        insert_text_to_doc(document_id, text)
        st.write("Text inserted in the document.")
