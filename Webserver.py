from flask import Flask
from threading import Thread

app = Flask(__name__)

kill = False

@app.route("/")
def main():
    return "Bot is running."

def server():
    print("Server code running.")
    global kill
    server = Thread(target=run)
    server.start()
    while True:
        if kill:
            print("Webserver Dying.")
            break
        print("Webserver Alive.")

def kill():
    print("Proceeding to kill webserver.")
    global kill
    kill = True

def run():
    app.run(host="0.0.0.0", port=8080)
    print("Webserver is ready.")
