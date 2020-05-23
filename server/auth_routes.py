"""
Manages the routes for user authentication and session management.
"""

from flask import Blueprint, render_template, redirect, url_for, request, flash, Markup
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from .user_model import User, load_user_by_email
from . import db


auth = Blueprint("auth", __name__)


@auth.route("/login")
def login():
    """
    The login page of the site.
    """
    return render_template("login.html", title="Log In")


@auth.route("/login", methods=["POST"])
def login_post():
    email = request.form.get("email")
    password = request.form.get("password")
    remember = True if request.form.get("remember", False) else False

    user = load_user_by_email(email)

    # Check that the user exists, and that their password matches.
    if not user or not check_password_hash(user.password, password):
        flash("Please check your login details and try again.")
        return redirect(url_for('auth.login'))

    # Register that the user is logged in with the session manager.
    login_user(user, remember=remember)
    return redirect(url_for("main.profile", user_id=current_user.id))


@auth.route("/logout")
@login_required
def logout():
    """
    Can be accessed to logout the user.
    """
    logout_user()
    return redirect(url_for("main.home"))


@auth.route("/signup")
def signup():
    """
    The sign up page of the site.
    """
    return render_template("signup.html", title="Sign Up")


@auth.route("/signup", methods=["POST"])
def signup_post():
    """
    Called when the signup form is submitted.
    """
    email = request.form.get("email")
    name = request.form.get("name")
    password = request.form.get("password")

    if len(email) == 0:
        flash("No email address provided.")
        return redirect(url_for("auth.signup"))

    if len(name) == 0:
        flash("No name provided.")
        return redirect(url_for("auth.signup"))

    if len(password) == 0:
        flash("No password provided.")
        return redirect(url_for("auth.signup"))

    # Check if a user already exists with the given email.
    user = load_user_by_email(email)
    if user:
        flash(Markup("Email address already exists. Go to <a href=\"" + url_for("auth.login") + "\">login page</a>."))
        return redirect(url_for("auth.signup"))

    # Hash the password so plaintext version isn't saved.
    password_hash = generate_password_hash(password, method="sha256")

    # Create new user with the form data.
    new_user = User(
        email_address=email,
        name=name,
        password=password_hash
    )

    # Add the new user to the database.
    db.session.add(new_user)
    db.session.commit()

    login_user(new_user, remember=True)

    return redirect(url_for("main.profile", username=current_user.name))