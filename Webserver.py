import flask
from flask import Flask
from threading import Thread

app = Flask(__name__)

@app.route("/")
def main():
    return "Bot is running."

def server():
    server = Thread(target=run)
    server.start()

def run():
    app.run(host="0.0.0.0", port=8080)
