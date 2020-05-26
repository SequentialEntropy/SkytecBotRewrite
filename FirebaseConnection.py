import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import os
import datetime

# try:
#     from SetEnviron import environ
#     environ()
# except FileNotFoundError:
#     print("SetEnviron file not found. Make sure a .env file is present or environment variables are set instead.")

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

# doc_ref = db.collection("projects").document("newdoc")
# doc_ref.set({
#     "name": "Test Project"
# })

# emp_ref = db.collection("projects")
# projects = emp_ref.stream()
# for project in projects:
#     print("{} => {}".format(project.id, project.to_dict()))
#     print(project.to_dict()["estimated-time"].strftime("%b %d %Y %H:%M:%S"))
#     print(project.to_dict()["estimated-time"].strftime("%b %d %Y"))
#     print(project.to_dict()["estimated-time"].day)
#     print(project.to_dict()["estimated-time"].month)
#     print(project.to_dict()["estimated-time"].year)
#     print(type(project.to_dict()["estimated-time"]))

def firebasefetch(collection):
    global db
    documents = db.collection(collection).stream()
    return [document.to_dict() for document in documents]
    
print(firebasefetch("projects"))