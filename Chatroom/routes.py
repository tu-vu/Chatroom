""" Routes for page content """
from flask import Blueprint, render_template, request, flash, jsonify
from flask_login import current_user, login_required
from flask_socketio import emit
from .models import *
from .import socketio

# Blueprint Configuration
main_bp = Blueprint(
    'main_bp', __name__,
    template_folder='templates',
    static_folder='static'
)

@main_bp.route("/dashboard", methods=["GET", "POST"])
@login_required
def dashboard(): 
    return render_template("dashboard.html")

### CREATE NEW CHANNEL ###
@main_bp.route("/add_channel", methods=["POST"])
def add_channel():
    channel_name = request.form.get("channel_name")

    # Check if the channel already exists in database
    existing_channel = Channel.query.filter_by(name=channel_name).first()

    # Only add new channel
    if existing_channel is None:
        # Create new channel associated with current_user
        current_user.create_channel(channel_name)
        return jsonify({"success": True})
    else:
        return jsonify({"success": False})

### LOAD ALL CHANNELS ASSOCIATING WITH USER ###
@main_bp.route("/load_channels", methods=["GET"])
def load_channels():
    # Get a JSON serialized version of channels
    channels = [channel.name for channel in current_user.channels]

    return jsonify({"channels": channels})

### SEND A NEW MESSAGE IN A CHANNEL ###
@main_bp.route("/add_message", methods=["POST"])
def add_message():
    message = request.form.get("message")
    channel_name = request.form.get("channel_name")

    # Get channel id
    channel_id = Channel.query.filter_by(name=channel_name).first().id

    # Add message to database
    timestamp = current_user.send_message(message=message, channel_id=channel_id)

    return jsonify({"author": current_user.username, "timestamp": timestamp.strftime('%H:%M')})

### LOAD MESSAGE HISTORY OF A CHANNEL ###
@main_bp.route("/load_messages", methods=["POST"])
def load_messages():
    channel_name = request.form.get("channel_name")

    # Get channel info
    channel = Channel.query.filter_by(name=channel_name).first()

    messages = []

    # Get a JSON serialized version of message history from database
    for message in channel.messages:
        # Initialize a JSON object
        msg = {"message": message.message,
               "author": message.author,
               "timestamp": message.timestamp.strftime('%H:%M')
            }

        # Append message to array
        messages.append(msg)

    return jsonify({"channel_name": channel_name, "messages": messages})

@socketio.on("send message")
def send_message(data):
    # Retrieve info of message
    message = data["message"]
    author = data["author"]
    timestamp = data["timestamp"]

    # Broadcast the message to all users in that channel
    emit("announce message", {"message": message, "author": author, "timestamp": timestamp}, broadcast=True)


