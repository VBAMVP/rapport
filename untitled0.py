import streamlit as st
from google.oauth2 import id_token
from google.auth.transport import requests
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import os

def create_google_doc(doc_title, creds):
    try:
        docs_service = build('docs', 'v1', credentials=creds)
        document = docs_service.documents().create(body={'title': doc_title}).execute()
        return document.get('documentId')
    except Exception as e:
        print(e)
        st.error(f"Une erreur est survenue lors de la création du document : {e}")
        return None

def upload_image_to_drive(image_path, creds):
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
    try:
        docs_service = build('docs', 'v1', credentials=creds)
        end_index = 1
        requests = [{'insertText': {'location': {'index': end_index}, 'text': text}}]
        docs_service.documents().batchUpdate(documentId=document_id, body={'requests': requests}).execute()
    except Exception as e:
        print(e)
        st.error(f"Une erreur est survenue lors de l'insertion du texte : {e}")

def main():
    st.title("Google Docs Creator")

    # Google Authentication
    st.subheader("Google Authentication")
    client_id = "YOUR_CLIENT_ID"  # Replace with your OAuth client ID
    token = st.text_input("Enter your Google ID token", type="password")
    
    creds = None
    if st.button("Authenticate"):
        try:
            idinfo = id_token.verify_oauth2_token(token, requests.Request(), client_id)
            if idinfo['aud'] != client_id:
                raise ValueError("Invalid client ID")
            st.success(f"Authentication successful: {idinfo['name']}")
            # Initialize creds for further operations
            creds = idinfo
        except ValueError as e:
            st.error("Authentication failed")
            st.error(e)

    if creds:
        # Interface for Google Docs operations

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

if __name__ == "__main__":
    main()
