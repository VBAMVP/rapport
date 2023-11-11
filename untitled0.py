import streamlit as st
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
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

    return build('docs', 'v1', credentials=creds)

def create_google_doc(docs_service, doc_title):
    try:
        document = docs_service.documents().create(body={'title': doc_title}).execute()
        return document.get('documentId')
    except Exception as e:
        print(e)
        st.error(f"Une erreur est survenue lors de la création du document : {e}")
        return None

def main():
    st.title("Google Docs Creator")

    client_secret = st.text_input("Enter your Google client secret", type="password")
    refresh_token = st.text_input("Enter your Google refresh token", type="password")

    if client_secret and refresh_token:
        docs_service = create_google_service(client_secret, refresh_token)

        # Interface pour créer un nouveau document
        with st.form("create_doc"):
            doc_title = st.text_input("Enter the title for the new document")
            submitted1 = st.form_submit_button("Create Document")
            if submitted1:
                document_id = create_google_doc(docs_service, doc_title)
                if document_id:
                    st.write(f"Document created with ID: {document_id}")

if __name__ == "__main__":
    main()
