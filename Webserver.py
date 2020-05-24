from flask import Flask
from threading import Thread

app = Flask(__name__)

@app.route("/")
def main():
    return "Bot is running."

def server():
    print("Server code running.")
    server = Thread(target=run)
    server.start()

def kill():
    print("Proceeding to kill webserver.")
    raise RuntimeError("Shutting down server")
    print("Shutting down server, RuntimeError raised")

def run():
    try:
        app.run(host="0.0.0.0", port=8080)
        print("Webserver is ready.")
    except RuntimeError, msg:
        if str(msg) == "Shutting down server":
            print("Shutting down server, RuntimeError caught")
