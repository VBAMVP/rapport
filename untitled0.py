import streamlit as st
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import os
import google_auth_httplib2
import httplib2

# Remplacez ceci par vos propres informations d'authentification
CLIENT_ID = "617474917009-egh3ngbg23ti3a3ju2ejdm18kr0pue0n.apps.googleusercontent.com"
CLIENT_SECRET = "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"

def create_google_service(refresh_token):
    creds = Credentials(None, refresh_token=refresh_token, token_uri='https://oauth2.googleapis.com/token', client_id=CLIENT_ID, client_secret=CLIENT_SECRET)
    http = creds.authorize(httplib2.Http())
    creds.refresh(google_auth_httplib2.Request(http))
    return build('docs', 'v1', credentials=creds), build('drive', 'v3', credentials=creds)

def create_google_doc(docs_service, doc_title):
    try:
        document = docs_service.documents().create(body={'title': doc_title}).execute()
        return document.get('documentId')
    except Exception as e:
        print(e)
        st.error(f"Une erreur est survenue lors de la création du document : {e}")
        return None

def upload_image_to_drive(drive_service, image_path):
    try:
        file_metadata = {'name': os.path.basename(image_path), 'mimeType': 'image/png'}
        media = MediaFileUpload(image_path, mimetype='image/png')
        file = drive_service.files().create(body=file_metadata, media_body=media, fields='id').execute()
        return file.get('id')
    except Exception as e:
        print(e)
        st.error(f"Une erreur est survenue lors du téléchargement de l'image : {e}")
        return None

def insert_image_to_doc(docs_service, document_id, image_id):
    try:
        requests = [{'insertInlineImage': {
                        'location': {'index': 1},
                        'uri': f'https://drive.google.com/uc?id={image_id}',
                        'objectSize': {'height': {'magnitude': 50, 'unit': 'PT'}, 'width': {'magnitude': 50, 'unit': 'PT'}}}}]
        docs_service.documents().batchUpdate(documentId=document_id, body={'requests': requests}).execute()
    except Exception as e:
        print(e)
        st.error(f"Une erreur est survenue lors de l'insertion de l'image : {e}")

def insert_text_to_doc(docs_service, document_id, text):
    try:
        end_index = 1
        requests = [{'insertText': {'location': {'index': end_index}, 'text': text}}]
        docs_service.documents().batchUpdate(documentId=document_id, body={'requests': requests}).execute()
    except Exception as e:
        print(e)
        st.error(f"Une erreur est survenue lors de l'insertion du texte : {e}")

def main():
    st.title("Google Docs Creator")

     refresh_token = st.text_input("Enter your Google refresh token", type="password")
     if refresh_token:
         docs_service, drive_service = create_google_service(refresh_token)

    
    
        # Création des services Google Docs et Drive avec le token de rafraîchissement
        docs_service, drive_service = create_google_service()
    
        # Interface pour créer un nouveau document
        with st.form("create_doc"):
            doc_title = st.text_input("Enter the title for the new document")
            submitted1 = st.form_submit_button("Create Document")
            if submitted1:
                document_id = create_google_doc(docs_service, doc_title)
                if document_id:
                    st.write(f"Document created with ID: {document_id}")
    
        # Interface pour télécharger et insérer une image
        with st.form("upload_image"):
            image_file = st.file_uploader("Upload an image", type=['png', 'jpg', 'jpeg'])
            submitted2 = st.form_submit_button("Upload and Insert Image")
            if submitted2 and image_file:
                image_path = image_file.name
                with open(image_path, "wb") as f:
                    f.write(image_file.getbuffer())
                image_id = upload_image_to_drive(drive_service, image_path)
                if image_id:
                    insert_image_to_doc(docs_service, document_id, image_id)
                    st.write("Image inserted in the document.")
    
        # Interface pour insérer du texte
        with st.form("insert_text"):
            text = st.text_area("Enter text to insert into the document")
            submitted3 = st.form_submit_button("Insert Text")
            if submitted3:
                insert_text_to_doc(docs_service, document_id, text)
                st.write("Text inserted in the document.")
    
    if __name__ == "__main__":
        main()
