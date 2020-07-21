############################ SET UP ############################
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_socketio import SocketIO
from config import Config

# Global accessible libraries
db = SQLAlchemy()
login_manager = LoginManager()
socketio = SocketIO(cors_allowed_origins="*", logger=True, engineio_logger=True)

def create_app():
    """ Initialize the core application """
    app = Flask(__name__, instance_relative_config=False)
    app.config.from_object(Config)

    # Initialize Plugins
    db.init_app(app)
    login_manager.init_app(app)
    socketio.init_app(app)

    with app.app_context():
        from . import routes
        from . import auth

        # Register Blueprints
        app.register_blueprint(routes.main_bp)
        app.register_blueprint(auth.auth_bp)

        # Create Database Models
        db.create_all()

        # Close the sql pool connections so that new forks create their own connection.
        db.session.remove()
        db.engine.dispose()
        return app