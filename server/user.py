#
# Holds the database models for the server.
#

from functools import wraps
from flask import render_template, flash
from flask_login import UserMixin, current_user
from . import db, login_manager
from .errors import forbidden


@login_manager.user_loader
def load_user(user_id):
    """ Loads the user data from the database, given their user ID. """
    return User.query.get(int(user_id))


def load_user_by_email(email):
    """ Loads the user data from the database, given their email. """
    return User.query.filter_by(email_address=email).first()


def load_all_users():
    """ Loads all of the users registered in the database. """
    return User.query.all()


def has_role(*roles):
    """ Returns whether the current user has any of the given roles. """
    return current_user.role in roles

def requires_role(*roles):
    """ An annotation that makes sure the current user has one of the given roles. """
    def decorator(func):
        @wraps(func)
        def decorated(*args, **kwargs):
            # If the user is not logged in, take them to the login page.
            if not current_user.is_authenticated:
                return login_manager.unauthorized()

            # If the user does not have the correct role, tell them.
            if not has_role(*roles):
                return forbidden()

            # Return the page.
            return func(*args, **kwargs)
        return decorated
    return decorator



class User(UserMixin, db.Model):
    """ Each registered user of the website. """
    __tablename__ = 'users'

    # The internal key assigned for each user.
    id = db.Column(db.Integer, primary_key=True)

    # User authentication fields.
    email_address = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))

    # User fields.
    name = db.Column(db.String(100))
    role = db.Column(db.String(16))
