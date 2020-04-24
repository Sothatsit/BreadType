#
# The main entry-point to the server.
#

from flask import Blueprint, render_template, send_from_directory, current_app

main = Blueprint('main', __name__)

@main.route('/')
def home():
    """
    The home page of the site.
    """
    return render_template("home.html", title="Home")

@main.route('/<path:path>')
def static_resources(path):
    """
    Responds to requests for static resources (e.g. stylesheets, javascript, images).

    Matches to any URLs not matched by the other routes.
    """
    return send_from_directory(current_app.static_folder, path)
