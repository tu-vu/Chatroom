""" Application entry point. """
from Chatroom import create_app
from Chatroom import socketio

app = create_app()

if __name__ == "__main__":
    socketio.run(app)