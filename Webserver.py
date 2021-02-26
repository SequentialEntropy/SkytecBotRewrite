from flask import Flask, jsonify
from flask_cors import CORS, cross_origin
from threading import Thread
import time

try:
    import FirebaseConnection
except FileNotFoundError:
    print("FirebaseConnection file not found. Website will not be able to access the database.")

app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

@app.route("/")
def main():
    global updatedprojects
    projecttext = "\n".join([("Project Name: {}, Project Description: {}, Estimate Time Completion: {}".format(project["name"], project["description"], project["estimated-time"].strftime("%b %d %Y"))) for project in updatedprojects])
    text = "Bot is running.\n" + projecttext
    return text

@app.route("/projects/")
@cross_origin()
def projects():
    global updatedprojects
    print(str(updatedprojects))
    return jsonify(updatedprojects)

def server():
    print("Server code running.")
    firebaselink = Thread(target=firebaseupdate)
    firebaselink.daemon = True
    firebaselink.start()
    serverinfolink = Thread(target=serverinfoupdate)
    serverinfolink.daemon = True
    serverinfolink.start()
    time.sleep(1)
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
        time.sleep(3600)

def serverinfoupdate():
    try:
        import ServerInfoModule
        global servers
        servers = {
            "lobby": {
                "api": ServerInfoModule.Server("lobby.alttd.com"),
                "color": 0x969c9f
            },
            "valley": {
                "api": ServerInfoModule.Server("valley.alttd.com", "vmap.alttd.com", "115survival"),
                "color": 0xf700ff
            },
            "summit": {
                "api": ServerInfoModule.Server("summit.alttd.com", "smap.alttd.com", "115survival"),
                "color": 0x00c9ff
            },
            "meadow": {
                "api": ServerInfoModule.Server("meadow.alttd.com", "mmap.alttd.com", "115survival"),
                "color": 0x00fe5d
            },
            "atoll": {
                "api": ServerInfoModule.Server("atoll.alttd.com", "amap.alttd.com", "115survival"),
                "color": 0xe8ff00
            },
            "creative": {
                "api": ServerInfoModule.Server("creative.alttd.com"),
                "color": 0x969c9f
            },
            "events": {
                "api": ServerInfoModule.Server("events.alttd.com"),
                "color": 0x969c9f    
            }
        }
        for server in servers:
            servers[server]["api"].update()
            print(str(servers[server]["api"].info))
    except FileNotFoundError:
        print("ServerInfoModule file not found. Bot will not ping servers.")

def run():
    try:
        app.run(host="0.0.0.0", port=8080)
        print("Webserver is ready.")
    except RuntimeError:
        print("Shutting down server, RuntimeError caught")
    return