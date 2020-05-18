"""
Manages the routes for the quiz entry-points to the website.
"""

from flask_login import login_required, current_user
from flask import Blueprint, render_template, send_from_directory, current_app, flash, request, redirect, url_for
from .user_model import requires_role
from .quiz_model import load_quiz, create_db_quiz
from .question_types import Question
from .error_routes import not_found


quiz = Blueprint("quiz", __name__)


@quiz.route("/quiz/<int:quiz_id>")
def take_quiz(quiz_id):
    """
    The page for taking the quiz with the given quiz id.
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


@quiz.route("/quiz/create")
@login_required
def create_quiz():
    """
    The page for creating a new quiz.
    """
    return render_template(
        "create_quiz.html",
        title="Create Quiz",
        previous=request.form
    )


@quiz.route("/quiz/create", methods=["POST"])
@login_required
def submit_create_quiz():
    """
    Called when the quiz create form has been submitted.
    """
    title = request.form.get("title")
    questions = Question.parse_many(request.form.get("questions"))

    # Check that a title has been supplied.
    if len(title) == 0:
        flash("Please enter a title.")
        return create_quiz()

    # Check that at least one question has been supplied.
    if len(questions) == 0:
        flash("Please enter some questions.")
        return create_quiz()

    # Check for any invalid questions.
    any_invalid = False
    for index, question in enumerate(questions):
        if question.is_valid:
            continue

        any_invalid = True
        flash("Could not parse question {}: {}".format(index, question.error))

    if any_invalid:
        return create_quiz()

    # Create the quiz!
    quiz = create_db_quiz(current_user.id, title, questions)
    if quiz is None:
        flash("There was an error creating the quiz.")
        return create_quiz()

    # Take the user to the quiz they created.
    return redirect(url_for("quiz.take_quiz", quiz_id=quiz.id))



@quiz.route("/quiz/<int:quiz_id>/edit")
@login_required
def edit_quiz(quiz_id):
    """
    The page for taking the quiz with the given quiz id.
    """
    quiz = load_quiz(quiz_id)
    if quiz is None:
        flash("The quiz you were looking for could not be found.")
        return not_found()

    # Render the quiz page.
    return render_template(
        "quiz.html",
        title="Edit Quiz",
        quiz_name=quiz.name,
        quiz_id=quiz.id,
        questions=enumerate(quiz.get_questions())
    )


@quiz.route("/quiz/<int:quiz_id>", methods=["POST"])
def submit_quiz(quiz_id):
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
    flash("Your answers: this is the tests" + ", ".join(["None" if a is None else a for a in answers]))
    return not_found()

@quiz.route("/quiz/view")
def view_quiz():
    """
    The page for viewing all currently created quizes
    """
    return render_template(
        "view_quiz.html",
        title="View Quiz",
        previous=request.form
    )