"""
Holds the command interfaces to the website.

These commands can be run directly through:
  ./run.sh prod <command>
However, many of the commands have shorthands in run.sh so that the "prod" is unnecessary.
"""

import click
from flask.cli import with_appcontext
from . import db
from .user_model import load_user_by_email, load_all_users


def add_commands(app):
    """ Register the commands with the Flask application. """
    app.cli.add_command(list_users)
    app.cli.add_command(set_role)
    app.cli.add_command(clear_role)
    app.cli.add_command(get_role)


@click.command("list-users")
@with_appcontext
def list_users():
    """ Lists all registered users. """
    users = load_all_users()
    if len(users) == 0:
        click.echo("There are no registered users.")
        return

    click.echo("Loaded all " + str(len(users)) + " registered users.\n")
    click.echo("email,name,role")
    for user in users:
        click.echo(user.email_address + "," + user.name + "," + ("" if user.role is None else user.role))


@click.command("set-role")
@click.argument("email")
@click.argument("role")
@with_appcontext
def set_role(email, role):
    """ Set the role of a user. """
    user = load_user_by_email(email)
    if not user:
        click.echo("Unable to find a user with the email:\n  " + email)
        return

    user.role = role
    db.session.commit()

    click.echo("The user " + email + " has been given the role:\n  " + role)


@click.command("clear-role")
@click.argument("email")
@with_appcontext
def clear_role(email):
    """ Clear the role of a user. """
    user = load_user_by_email(email)
    if not user:
        click.echo("Unable to find a user with the email:\n  " + email)
        return

    user.role = None
    db.session.commit()

    click.echo("The role of the user " + email + " has been cleared.")


@click.command("get-role")
@click.argument("email")
@with_appcontext
def get_role(email):
    """ Get the role of a user. """
    user = load_user_by_email(email)
    if not user:
        click.echo("Unable to find a user with the email:\n  " + email)
        return

    if user.role is not None:
        click.echo("The user " + email + " has the role:\n  " + user.role)
    else:
        click.echo("The user " + email + " has no role.")
