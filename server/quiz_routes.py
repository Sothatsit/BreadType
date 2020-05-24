"""
Manages the routes for the quiz entry-points to the website.
"""

import uuid
from flask_login import login_required, current_user
from flask import Blueprint, render_template, send_from_directory, current_app, flash, request, redirect, url_for
from .user_model import has_role, save_answer_set
from .quiz_model import load_quiz, load_all_quizzes, create_db_quiz, edit_db_quiz, delete_db_quiz
from .error_routes import not_found, forbidden, message_page
from .quiz import Quiz, AnswerSet
from .question import MultiChoiceQuestion, IntSliderQuestion, FloatSliderQuestion


quiz = Blueprint("quiz", __name__)


def can_edit_quiz(quiz):
    """ Returns whether the current user can edit the given quiz. """
    return current_user.is_authenticated and (has_role("admin") or quiz.owner.id == current_user.id)


@quiz.route("/quiz/view")
def view_quiz():
    """
    The page for viewing all currently created quizes
    """
    quizzes = load_all_quizzes()
    return render_template(
        "view_quiz.html",
        title="View Quiz",
        quizzes=quizzes,
        previous=request.form
    )


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
        quiz=quiz,
        can_edit_quiz=can_edit_quiz(quiz),
        answers_uuid=str(uuid.uuid4())
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

    # Read the answers that the user gave from the form.
    answer_set = AnswerSet.read_from_form(current_user, quiz, request.form)

    # Save the answers in the database.
    save_answer_set(answer_set)

    # Score the user's responses against the categories.
    category_scores = answer_set.score_answers()
    best_category = answer_set.find_best_matching_category()

    # Render the results page.
    return render_template(
        "quiz_results.html",
        title="Your Results",
        category=best_category,
        category_scores=category_scores
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
    # Stores any errors that happen during parsing.
    errors = []

    # Parse the quiz from the form.
    quiz = Quiz.from_form(current_user, request.form, errors)
    if len(errors) > 0:
        for error in errors:
            flash(error)
        return create_quiz()

    # Create the quiz in the database.
    errors = create_db_quiz(quiz)
    if len(errors) > 0:
        for error in errors:
            flash(error)
        return create_quiz()

    # Take the user to the quiz they created.
    return redirect(url_for("quiz.take_quiz", quiz_id=quiz.id))


def render_edit_quiz(quiz):
    """
    Returns the rendered edit quiz page for the given quiz.
    """
    return render_template(
        "edit_quiz.html",
        title="Edit Quiz",
        quiz_id=quiz.id,
        quiz_title=request.form.get("title", quiz.name),
        questions_text=request.form.get("encoded_text", quiz.encode())
    )


@quiz.route("/quiz/<int:quiz_id>/edit")
@login_required
def edit_quiz(quiz_id):
    """
    The page for taking the quiz with the given quiz id.
    """
    # Find the quiz.
    quiz = load_quiz(quiz_id)
    if quiz is None:
        flash("The quiz you were looking for could not be found.")
        return not_found()

    # Check that the user has permission to edit this quiz.
    if not can_edit_quiz(quiz):
        flash("You do not have permission to edit this quiz.")
        return forbidden()

    # Render the edit quiz page.
    return render_edit_quiz(quiz)


@quiz.route("/quiz/<int:quiz_id>/edit", methods=["POST"])
@login_required
def submit_edit_quiz(quiz_id):
    """
    Called when the user has submitted changes to the quiz.
    """
    # Find the quiz.
    old_quiz = load_quiz(quiz_id)
    if old_quiz is None:
        flash("The quiz you were looking for could not be found.")
        return not_found()

    # Check that the user has permission to edit this quiz.
    if not can_edit_quiz(old_quiz):
        flash("You do not have permission to edit this quiz.")
        return forbidden()

    # Get the fields that the user may have changed.
    title = request.form.get("title")
    encoded_text = request.form.get("encoded_text")
    new_quiz = Quiz.parse(-1, title, current_user, encoded_text)

    # Update the quiz!
    errors = edit_db_quiz(old_quiz, new_quiz)
    if len(errors) > 0:
        for error in errors:
            flash(error)
        return render_edit_quiz(old_quiz)

    # Take the user to the edited quiz.
    return redirect(url_for("quiz.take_quiz", quiz_id=old_quiz.id))


@quiz.route("/quiz/<int:quiz_id>/delete")
@login_required
def delete_quiz(quiz_id):
    """
    If a user navigates to this page and has permission, deletes the quiz.
    """
    # Find the quiz.
    quiz = load_quiz(quiz_id)
    if quiz is None:
        flash("The quiz you were looking for could not be found.")
        return not_found()

    # Check that the user has permission to edit this quiz.
    if not can_edit_quiz(quiz):
        flash("You do not have permission to delete this quiz.")
        return forbidden()

    # Delete the quiz.
    errors = delete_db_quiz(quiz)
    if len(errors) > 0:
        for error in errors:
            flash(error)
        return message_page("Error deleting quiz")

    # Tell the user the quiz has been deleted.
    message = "The quiz \"{}\" has been deleted.".format(quiz.name)
    return message_page("Quiz Deleted", message)

