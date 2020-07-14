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
@main_bp.route("/create", methods=["POST"])
def create():
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
@main_bp.route("/load", methods=["GET"])
def load():
    # Get a JSON serialized version of channels(basically a list of strings)
    channels = [channel.name for channel in current_user.channels]

    return jsonify({"channels": channels})

### SEND A NEW MESSAGE IN A CHANNEL ###
# @main_bp.route("/send_message", method=["POST"])
# def send_message():
#     pass

