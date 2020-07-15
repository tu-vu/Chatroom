""" Routes for page content """
from flask import Blueprint, url_for, render_template, request, redirect, flash, jsonify
from flask_login import current_user, login_required
from .forms import *
from .models import *
from .import Config
import requests

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

    # Get channel info
    channel = Channel.query.filter_by(name=channel_name).first()

    # Add message to database
    current_user.send_message(message=message, channel_id=channel.id)

    return jsonify({"message": message})

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
        msg = dict()
        msg["message"] = message.message
        msg["author"] = message.author
        msg["timestamp"] = message.timestamp

        # Append it to our array
        messages.append(msg)

    return jsonify({"channel_name": channel_name, "messages": messages})
