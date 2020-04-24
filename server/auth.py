#
# Manages user sessions.
#

from flask import Blueprint, render_template

auth = Blueprint('auth', __name__)

@auth.route('/login')
def login():
    """
    The login page of the site.
    """
    return render_template("login.html", title="Log In")
