import flask
from flask import Flask
from threading import Thread

app = Flask(__name__)

kill = False

@app.route("/")
def main():
    return "Bot is running."

def server():
    global kill
    server = Thread(target=run)
    server.start()
    while True:
        if kill:
            break

def kill():
    global kill
    kill = True

def run():
    app.run(host="0.0.0.0", port=8080)
