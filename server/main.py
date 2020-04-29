#
# The main entry-point to the server.
#

from flask_login import login_required, current_user
from flask import Blueprint, render_template, send_from_directory, current_app
from .user import requires_role

main = Blueprint("main", __name__)

@main.route("/")
def home():
    """ The home page of the site. """
    return render_template("home.html", title="Home")

@main.route("/profile")
@login_required
def profile():
    """ A profile page for each user. """
    return render_template("profile.html", title="Profile", name=current_user.name)

@main.route("/admin")
@requires_role("admin")
def admin():
    return render_template("profile.html", title="Admin", name="admin")

@main.route("/<path:path>")
def static_resources(path):
    """
    Responds to requests for static resources (e.g. stylesheets, javascript, images).

    Matches to any URLs not matched by the other routes.
    """
    return send_from_directory(current_app.static_folder, path)
