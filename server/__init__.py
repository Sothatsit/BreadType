import yaml
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

# The database that holds persistent information for this website.
db = SQLAlchemy()

# Manages sessions for the website.
login_manager = LoginManager()

# Load the config
with open("config.yml", 'r') as stream:
    config = yaml.safe_load(stream)

def create_app():
    # Create the app.
    app = Flask(__name__, template_folder="../client/templates", static_folder="../client/static")

    # Set up the configuration for the Flask app.
    app.config["SECRET_KEY"] = config["secret-key"]
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///../db.sqlite"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # Register the cli commands.
    from .cli import add_commands
    add_commands(app)

    # Register the error page handlers.
    from .errors import register_error_handlers
    register_error_handlers(app)

    # Initialise the database of the website.
    db.init_app(app)

    # Make sure all database tables are created.
    from .user import User
    with app.app_context():
        db.create_all()

    # Initialise the login session manager for the website.
    login_manager.login_view = "auth.login"
    login_manager.init_app(app)

    # Register the method to get the data for a user.
    from .user import load_user

    # Blueprint for authentication routes in our app.
    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)

    # Blueprint for non-authentication parts of app.
    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    return app
