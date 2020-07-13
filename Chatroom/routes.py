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
def dashboard(): 
    return render_template("dashboard.html")

''' CREATE NEW CHANNEL '''
@main_bp.route("/create", methods=["POST"])
def create():
    channel_name = request.form.get("channel_name")

    # Check if the channel already exists in database
    existing_channel = Channel.query.filter_by(name=channel_name).first()

    # Only add new channel
    if existing_channel is None:
        new_channel = Channel(name=channel_name)
        db.session.add(new_channel)
        db.session.commit()
        return jsonify({"success": True})
    else:
        return jsonify({"success": False})
