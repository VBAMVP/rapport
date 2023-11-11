import streamlit as st
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import os
from google.auth.transport.requests import Request

# Remplacez ceci par votre ID client OAuth
CLIENT_ID = "617474917009-egh3ngbg23ti3a3ju2ejdm18kr0pue0n.apps.googleusercontent.com"

def create_google_service(client_secret, refresh_token):
    creds = Credentials(
        None, 
        refresh_token=refresh_token, 
        token_uri='https://oauth2.googleapis.com/token', 
        client_id=CLIENT_ID, 
        client_secret=client_secret
    )

    # Rafraîchir explicitement le token
    creds.refresh(Request())

    return build('docs', 'v1', credentials=creds), build('drive', 'v3', credentials=creds)

def create_google_doc(docs_service, doc_title):
    # (Votre fonction create_google_doc inchangée)

def upload_image_to_drive(drive_service, image_path):
    # (Votre fonction upload_image_to_drive inchangée)

def insert_image_to_doc(docs_service, document_id, image_id):
    # (Votre fonction insert_image_to_doc inchangée)

def insert_text_to_doc(docs_service, document_id, text):
    # (Votre fonction insert_text_to_doc inchangée)

def main():
    st.title("Google Docs Creator")

    client_secret = st.text_input("Enter your Google client secret", type="password")
    refresh_token = st.text_input("Enter your Google refresh token", type="password")

    if client_secret and refresh_token:
        docs_service, drive_service = create_google_service(client_secret, refresh_token)

        # Interface pour créer un nouveau document
        with st.form("create_doc"):
            # (Votre code de création de document inchangé)

        # Interface pour télécharger et insérer une image
        with st.form("upload_image"):
            # (Votre code de téléchargement et insertion d'image inchangé)

        # Interface pour insérer du texte
        with st.form("insert_text"):
            # (Votre code d'insertion de texte inchangé)

if __name__ == "__main__":
    main()
