"""
Manages the routes for the main entry-points to the website.
"""

from flask_login import login_required, current_user
from flask import Blueprint, render_template, send_from_directory, current_app, flash, request
from .user_model import requires_role
from .quiz_model import load_quiz
from .error_routes import not_found


main = Blueprint("main", __name__)


@main.route("/")
def home():
    """ The home page of the site. """
    return render_template("home.html", title="Home")


@main.route("/profile/<username>")
@login_required
def profile(username):
    """ A profile page for each user. """
    # figure out how to only show quizes by that user
    #conn = sqlite3.connect("db.sqlite")
    #cur = conn.cursor()
    #cur.execute("SELECT * FROM `quiz`")
    #rows = cur.fetchall()
    #cur.execute("SELECT user.name FROM `user` INNER JOIN `quiz` ON user.id = quiz.owner")
    #names = cur.fetchall()
    return render_template("profile.html", title=username + "'s Profile", name=username)


@main.route("/admin")
@requires_role("admin")
def admin():
    """ Not actually useful, just for testing @requires_role. """
    return render_template("profile.html", title="Admin", name="admin")


@main.route("/<path:path>")
def static_resources(path):
    """
    Responds to requests for static resources (e.g. stylesheets, javascript, images).

    Matches to any URLs not matched by the other routes.
    """
    return send_from_directory(current_app.static_folder, path)
