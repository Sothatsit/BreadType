"""
Manages the routes for responding with errors to the user.
"""

#
# The error pages of the server.
#

from flask import Blueprint, render_template, flash


errors = Blueprint("errors", __name__)


def register_error_handlers(app):
    """ Registers the error page handlers with the Flask application. """
    app.register_error_handler(403, forbidden)
    app.register_error_handler(404, not_found)


def error_page(error_code, error_name, error_message):
    """ Renders the error page for the given error. """
    error_title = str(error_code) + ": " + error_name
    template = render_template(
        "error.html",
        title=error_name,
        error_title=error_title,
        error_message=error_message
    )
    return template, error_code


def forbidden(e="ignored"):
    """ The 403 page. """
    return error_page(403, "Forbidden", "You do not have permission to view this page.")


def not_found(e="ignored"):
    """ The 404 page. """
    return error_page(404, "Not Found", "The page you were looking for could not be found.")