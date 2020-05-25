"""
Manages the routes for the main entry-points to the website.
"""

from flask_login import login_required, current_user
from flask import Blueprint, render_template, send_from_directory, current_app, flash, request
from .user_model import requires_role, load_user, load_all_users
from .quiz_model import load_quiz, delete_db_quiz
from .error_routes import not_found, message_page
from . import db


main = Blueprint("main", __name__)


@main.route("/")
def home():
    """ The home page of the site. """
    return render_template("home.html", title="Home")


@main.route("/profile/<int:user_id>")
def profile(user_id):
    """ A profile page for each user. """
    user = load_user(user_id)
    if user is None:
        flash("The user you were looking for could not be found.")
        return not_found()

    return render_template(
        "profile.html",
        title=user.name + "'s Profile",
        name=user.name,
        quizzes=user.get_quizzes(),
        answer_sets=user.get_latest_answer_sets()
    )


@main.route("/admin")
@requires_role("admin")
def admin():
    """ Admin page to view all current users """
    users = load_all_users()
    return render_template("admin.html", 
        title="Admin", 
        users=users)


@main.route("/profile/<int:user_id>/delete")
@requires_role("admin")
def delete_user(user_id):
    """
    If a user navigates to this page and has permission, deletes the user.
    """
    # Find the user.
    user = load_user(user_id)
    if user is None:
        flash("The user you were looking for could not be found.")
        return not_found()

    # Find and delete all user's quizes
    quizzes = user.get_quizzes()
    for quiz in quizzes:
        delete_db_quiz(quiz)

    # Find and delete all user's answers
    for db_answer in user.db_answers:
        db.session.delete(db_answer)

    # Delete the user.
    db.session.delete(user)
    db.session.commit()
    
    # Tell the admin the user has been deleted.
    message = "The user \"{}\" has been deleted.".format(user.name)
    return message_page("User Deleted", message)


@main.route("/<path:path>")
def static_resources(path):
    """
    Responds to requests for static resources (e.g. stylesheets, javascript, images).

    Matches to any URLs not matched by the other routes.
    """
    return send_from_directory(current_app.static_folder, path)
