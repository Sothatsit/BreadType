"""
Contains the initialisation code for the Flask application.
"""

import yaml
from flask import Flask
from flask_login import LoginManager

from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate, MigrateCommand


# The database that holds persistent information for this website.
db = SQLAlchemy()


# Manages the user sessions for the website.
login_manager = LoginManager()


# Load the configuration for the website.
with open("config.yml", 'r') as stream:
    config = yaml.safe_load(stream)


def create_app():
    """
    Creates and initialises the Flask application.
    """

    # Create the app.
    app = Flask(__name__, template_folder="../client/templates", static_folder="../client/static")

    # Set up the configuration for the Flask app.
    app.config["SECRET_KEY"] = config["secret-key"]
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///../db.sqlite"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # Register the cli commands.
    from .commands import add_commands
    add_commands(app)

    # Register the error page handlers.
    from .error_routes import register_error_handlers
    register_error_handlers(app)

    # Initialise the database of the website.
    db.init_app(app)

    # Make sure all database tables are created.
    from .user_model import User
    from .quiz_model import Quiz
    from .quiz_model import QuizQuestion
    with app.app_context():
        db.create_all()

    # Register the database migration command.
    migrate = Migrate(app, db)
    app.cli.add_command("db", MigrateCommand)

    # Initialise the login session manager for the website.
    login_manager.login_view = "auth.login"
    login_manager.init_app(app)

    # Register the method to get the data for a user.
    from .user_model import load_user

    # Blueprint for authentication routes in our app.
    from .auth_routes import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)

    # Blueprint for non-authentication parts of the app.
    from .main_routes import main as main_blueprint
    app.register_blueprint(main_blueprint)

    # Blueprint for the quiz parts of the app.
    from .quiz_routes import quiz as quiz_blueprint
    app.register_blueprint(quiz_blueprint)

    return app
