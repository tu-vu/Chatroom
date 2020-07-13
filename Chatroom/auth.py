""" Routes for user authentication """
from flask import Blueprint, url_for, render_template, request, redirect, flash
from flask_login import current_user, login_user, logout_user, login_required
from .forms import SignupForm, LoginForm
from .models import db, User
from .import login_manager

# Blueprint Configuration
auth_bp = Blueprint(
    'auth_bp', __name__,
    template_folder='templates',
    static_folder='static'
)

@auth_bp.route("/signup", methods=["GET", "POST"])
def signup():
    """
    User sign-up page.
    GET requests serve sign-up page.
    POST requests validate form & user creation.
    """
    form = SignupForm()
    if form.validate_on_submit():
        # Users fill form correctly
        # Check if email already exists
        existing_user = User.query.filter_by(email=form.email.data).first()
        if existing_user is None:
            # Check if username already exists
            existing_username = User.query.filter_by(username=form.username.data).first()
            if existing_username is None:
                user = User(username=form.username.data, 
                            email=form.email.data, 
                            password=form.password.data)
                db.session.add(user)
                db.session.commit() # Create new user
                login_user(user) # Log in as newly created user - magically!
                # Go to movie dashboard page
                return redirect(url_for('main_bp.dashboard'))
            flash("Username already exists!")
        else:
            flash("A user already exists with that email address.")
    return render_template("signup.html", form=form)

@auth_bp.route("/", methods=["GET", "POST"])
def login():
    """
    Log-in page for registered users
    GET requests serve log-in page.
    POST requests validate and redirect user to dashboard page
    """
    # Bypass if user is already logged in 
    if current_user.is_authenticated:
        return redirect(url_for('main_bp.dashboard'))

    form = LoginForm()
    # Validate login attempt
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        # If user exists in our database and password matches
        if user and user.password == form.password.data:
            login_user(user) # Log in as existing user
            return redirect(url_for('main_bp.dashboard'))
        elif not user:
            flash("Account does not exists!")
        else:
            flash("Password does not match!")
    return render_template("login.html", form=form)

@auth_bp.route("/logout")
@login_required
def logout():
    """ User log-out logic. """
    logout_user()
    return redirect(url_for('auth_bp.login'))

# Given *user_id*, return the associated User object. 
# Also, we can access current user info via current_user.attribute
@login_manager.user_loader
def load_user(user_id):
    """ Check if user is logged-in on every page load. """
    if user_id:
        return User.query.get(user_id)
    return None

@login_manager.unauthorized_handler
def unauthorized():
    """ Redirect unauthorized users to Login page. """
    flash("You must be logged in to view that page")
    return redirect(url_for('auth_bp.login'))