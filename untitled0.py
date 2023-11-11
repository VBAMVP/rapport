# -*- coding: utf-8 -*-

import json
import streamlit as st
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import os

# Fonctions pour les opérations Google Docs et Drive
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

def create_google_doc(doc_title, creds):
    """Create a Google Doc with the given title."""
    try:
        docs_service = build('docs', 'v1', credentials=creds)
        document = docs_service.documents().create(body={'title': doc_title}).execute()
        return document.get('documentId')
    except Exception as e:
        print(e)  # Affiche l'erreur dans la console
        st.error(f"Une erreur est survenue : {e}")  # Affiche l'erreur dans l'interface Streamlit
        return None

def upload_image_to_drive(image_path, creds):
    """Upload an image to Google Drive and return its ID."""
    try:
        drive_service = build('drive', 'v3', credentials=creds)
        file_metadata = {'name': os.path.basename(image_path), 'mimeType': 'image/png'}
        media = MediaFileUpload(image_path, mimetype='image/png')
        file = drive_service.files().create(body=file_metadata, media_body=media, fields='id').execute()
        return file.get('id')
    except Exception as e:
        print(e)
        st.error(f"Une erreur est survenue lors du téléchargement de l'image : {e}")
        return None

def insert_image_to_doc(document_id, image_id, creds):
    """Insert an image into a Google Doc."""
    try:
        docs_service = build('docs', 'v1', credentials=creds)
        requests = [{'insertInlineImage': {
                        'location': {'index': 1},
                        'uri': f'https://drive.google.com/uc?id={image_id}',
                        'objectSize': {'height': {'magnitude': 50, 'unit': 'PT'}, 'width': {'magnitude': 50, 'unit': 'PT'}}}}]
        docs_service.documents().batchUpdate(documentId=document_id, body={'requests': requests}).execute()
    except Exception as e:
        print(e)
        st.error(f"Une erreur est survenue lors de l'insertion de l'image : {e}")

def insert_text_to_doc(document_id, text, creds):
    """Insert text into a Google Doc."""
    try:
        docs_service = build('docs', 'v1', credentials=creds)
        end_index = 1 # You might want to find the correct end index where to insert the text
        requests = [{'insertText': {'location': {'index': end_index}, 'text': text}}]
        docs_service.documents().batchUpdate(documentId=document_id, body={'requests': requests}).execute()
    except Exception as e:
        print(e)
        st.error(f"Une erreur est survenue lors de l'insertion du texte : {e}")

# Streamlit Interface
st.title('Google Docs Creator')

# Téléchargez le fichier client_secret.json
uploaded_file = st.file_uploader("Upload client_secret.json", type="json")
if uploaded_file is not None:
    creds_json = json.load(uploaded_file)
    creds = authenticate_google(creds_json)
    if creds:
         st.success("Authentification réussie!")
    else:
        st.error("Échec de l'authentification.")

# La logique de l'application vient ici
print("Creds:", creds)
# Formulaire pour créer un nouveau document
with st.form("create_doc"):
    doc_title = st.text_input("Enter the title for the new document")
    submitted1 = st.form_submit_button("Create Document")
    if submitted1:
        document_id = create_google_doc(doc_title, creds)
        if document_id:
            st.write(f"Document created with ID: {document_id}")

# Télécharger et insérer l'image
with st.form("upload_image"):
    image_file = st.file_uploader("Upload an image", type=['png', 'jpg', 'jpeg'])
    submitted2 = st.form_submit_button("Upload and Insert Image")
    if submitted2 and image_file:
        image_path = image_file.name
        with open(image_path, "wb") as f:
            f.write(image_file.getbuffer())
            image_id = upload_image_to_drive(image_path, creds)
            if image_id:
                insert_image_to_doc(document_id, image_id, creds)
                st.write("Image inserted in the document.")

# Formulaire pour insérer du texte
with st.form("insert_text"):
    text = st.text_area("Enter text to insert into the document")
    submitted3 = st.form_submit_button("Insert Text")
    if submitted3:
        insert_text_to_doc(document_id, text, creds)
        st.write("Text inserted in the document.")
