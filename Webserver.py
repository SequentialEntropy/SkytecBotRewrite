from flask import Flask, jsonify
from flask_cors import CORS, cross_origin
from threading import Thread
import time
import asyncio

try:
    import FirebaseConnection
except FileNotFoundError:
    print("FirebaseConnection file not found. Website will not be able to access the database.")

try:
    import ServerInfoModule
except FileNotFoundError:
    print("ServerInfoModule file not found. Bot will not ping servers.")

class FlaskWebserver:
    def __init__(self, ip="0.0.0.0", port=8080, parent=None):
        self.ip = ip
        self.port = port
        self._parent = parent
        self.app = Flask(__name__)
        self.cors = CORS(self.app)
        self.app.config["CORS_HEADERS"] = "Content-Type"
        self.server()

    def appaddresses(self):
        
        @self.app.route("/")
        def main():
            return "Bot and api are online."
        
        @self.app.route("/projects/")
        @cross_origin()
        def projects():
            return str(self.updatedprojects)

    def run(self):
        self.appaddresses()
        try:
            self.app.run(host=self.ip, port=self.port)
        except RuntimeError:
            print("Shutting down server, RuntimeError caught")

        
    def server(self):
        print("Server code running.")
        print("Firebase Linking.")
        self.firebaselink = Thread(target=self.firebaseupdate)
        self.firebaselink.daemon = True
        self.firebaselink.start()

        print("Server Info Linking.")
        self.serverinfolink = Thread(target=self.serverinfoupdate)
        self.serverinfolink.daemon = True
        self.serverinfolink.start()

        time.sleep(1)

        print("Server running.")
        self.serverrun = Thread(target=self.run)
        self.serverrun.daemon = True
        self.serverrun.start()

        print("Server started.")
        return

    def kill(self):
        print("Proceeding to kill webserver.")
        raise RuntimeError("Shutting down server")
        print("Shutting down server, RuntimeError raised")
        return

    def firebaseupdate(self):
        while True:
            self.updatedprojects = FirebaseConnection.firebasefetch("projects")
            if self.updatedprojects != None:
                print("Projects Updated")
            time.sleep(3600)

    def serverinfoupdate(self):
        self.servers = {
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
        print("Server updating.")
        while True:
            for server in self.servers:
                self.servers[server]["api"].update()
                print("{} Updated".format(server.capitalize()))
            if self._parent != None:
                loop = self._parent.event_loop
                # task = loop.create_task(self._parent.serverupdate())
                # asyncio.run_coroutine_threadsafe(task, loop)


                loop.call_soon_threadsafe(asyncio.ensure_future, self._parent.serverupdate())
            time.sleep(60)