""" Routes for page content """
from flask import Blueprint, url_for, render_template, request, redirect, flash
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
    username = request.form.get("username")
    return render_template("dashboard.html", username=username)