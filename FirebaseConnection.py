import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import os

cred = credentials.Certificate({
			  "type": "service_account",
			  "project_id": os.environ.get('PROJECT_ID'),
			  "private_key_id": os.environ.get('PRIVATE_KEY_ID'),
			  "private_key": os.environ.get('PRIVATE_KEY').replace('\\n', '\n'),
			  "client_email": os.environ.get('CLIENT_EMAIL'),
			  "client_id": os.environ.get('CLIENT_ID'),
			  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
			  "token_uri": "https://accounts.google.com/o/oauth2/token",
			  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
			  "client_x509_cert_url": os.environ.get('CLIENT_CERT_URL')
		})

firebase_admin.initialize_app(cred)
db = firestore.client()

def firebasefetch(collection):
    global db
    documents = db.collection(collection).stream()
    return [document.to_dict() for document in documents]