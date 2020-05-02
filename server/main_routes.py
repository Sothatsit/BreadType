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


@main.route("/profile")
@login_required
def profile():
    """ A profile page for each user. """
    return render_template("profile.html", title="Profile", name=current_user.name)


@main.route("/admin")
@requires_role("admin")
def admin():
    """ Not actually useful, just for testing @requires_role. """
    return render_template("profile.html", title="Admin", name="admin")


@main.route("/quiz/<int:quiz_id>")
def quiz(quiz_id):
    """
    The page for the quiz with the given quiz id.
    """
    quiz = load_quiz(quiz_id)
    if quiz is None:
        flash("The quiz you were looking for could not be found.")
        return not_found()

    # Render the quiz page.
    return render_template(
        "quiz.html",
        title="Quiz",
        quiz_name=quiz.name,
        quiz_id=quiz.id,
        questions=enumerate(quiz.get_questions())
    )


@main.route("/quiz/<int:quiz_id>", methods=["POST"])
def quiz_submit(quiz_id):
    """
    Called when the quiz with the given ID has been submitted.
    """
    quiz = load_quiz(quiz_id)
    if quiz is None:
        flash("The quiz you were looking for could not be found.")
        return not_found()

    # Extract the answers the user selected.
    answers = []
    for index, question in enumerate(quiz.get_questions()):
        answers.append(question.get_answer_from_form(request.form, index))

    # For now, just return the results using the not_found page for testing.
    flash("Your answers: " + ", ".join(["None" if a is None else a for a in answers]))
    return not_found()


@main.route("/<path:path>")
def static_resources(path):
    """
    Responds to requests for static resources (e.g. stylesheets, javascript, images).

    Matches to any URLs not matched by the other routes.
    """
    return send_from_directory(current_app.static_folder, path)
