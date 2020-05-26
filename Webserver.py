from flask import Flask, jsonify
from threading import Thread
import time

try:
    import FirebaseConnection
except FileNotFoundError:
    print("FirebaseConnection file not found. Website will not be able to access the database.")

app = Flask(__name__)

@app.route("/")
def main():
    global updatedprojects
    projecttext = "\n".join([("Project Name: {}, Project Description: {}, Estimate Time Completion: {}".format(project["name"], project["description"], project["estimated-time"].strftime("%b %d %Y"))) for project in updatedprojects])
    text = "Bot is running.\n" + projecttext
    return text

@app.route("/projects/")
def projects():
    global updatedprojects
    print(str(updatedprojects))
    return jsonify(updatedprojects)

def server():
    print("Server code running.")
    firebaselink = Thread(target=firebaseupdate)
    firebaselink.daemon = True
    firebaselink.start()
    time.sleep(3)
    server = Thread(target=run)
    server.daemon = True
    server.start()
    print("Server started")
    return

def kill():
    print("Proceeding to kill webserver.")
    raise RuntimeError("Shutting down server")
    print("Shutting down server, RuntimeError raised")
    return

def firebaseupdate():
    global updatedprojects
    while True:
        updatedprojects = FirebaseConnection.firebasefetch("projects")
        if updatedprojects != None:
            print("Projects Updated")
        time.sleep(86400)

def run():
    try:
        app.run(host="0.0.0.0", port=8080)
        print("Webserver is ready.")
    except RuntimeError:
        print("Shutting down server, RuntimeError caught")
    return
