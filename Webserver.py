from flask import Flask
from threading import Thread

app = Flask(__name__)

@app.route("/")
def main():
    return "Bot is running."

def server():
    print("Server code running.")
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

def run():
    try:
        app.run(host="0.0.0.0", port=8080)
        print("Webserver is ready.")
    except RuntimeError:
        print("Shutting down server, RuntimeError caught")
    return
