"""
Holds the database model for storing users, and code for verifying their role.
"""

from datetime import datetime
from functools import wraps
from flask_login import UserMixin, current_user
from . import db, login_manager
from .error_routes import forbidden
from .quiz import UserAnswer, AnswerSet
from .quiz_model import load_question, load_quiz


@login_manager.user_loader
def load_user(user_id):
    """ Loads the user data from the database, given their user ID. """
    return User.query.get(int(user_id))


def load_user_by_email(email):
    """ Loads the user data from the database, given their email. """
    return User.query.filter_by(email_address=email).first()


def load_all_users():
    """ Loads all of the users registered in the database. """
    return User.query.all()


def save_answer_set(answer_set):
    """ Saves the given answer set in the database. """
    # Check that this answer set does not already exist in the database.
    existing = DBUserAnswer.query.filter_by(uuid=answer_set.answers_uuid).first()
    if existing is not None:
        return

    # Add all of the answers to the database.
    for answer in answer_set.answers:
        db_answer = DBUserAnswer(
            uuid=answer.uuid,
            user_id=answer.user.id,
            question_id=answer.question.get_db_question().id,
            answer=answer.answer
        )
        answer.set_db_answer(db_answer)
        db.session.add(db_answer)

    # Commit the changes.
    db.session.commit()


def load_answers_of_question(question):
    """ Loads all answers that have been given to the given question. """
    db_answers = DBUserAnswer.query.filter_by(question_id=question.get_db_question().id).all()
    return [db_answer.get_user_answer(None, question) for db_answer in db_answers]


def has_role(*roles):
    """ Returns whether the current user has any of the given roles. """
    return current_user.is_authenticated and current_user.role in roles


def requires_role(*roles):
    """ An annotation that makes sure the current user has one of the given roles. """
    def decorator(func):
        @wraps(func)
        def decorated(*args, **kwargs):
            # If the user is not logged in, take them to the login page.
            if not current_user.is_authenticated:
                return login_manager.unauthorized()

            # If the user does not have the correct role, tell them.
            if not has_role(*roles):
                return forbidden()

            # Return the page.
            return func(*args, **kwargs)
        return decorated
    return decorator


class User(UserMixin, db.Model):
    """ The database entry for each registered user of the website. """
    __tablename__ = 'user'

    # The internal key assigned for each user.
    id = db.Column(db.Integer, primary_key=True, nullable=False)

    # User authentication fields.
    email_address = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)

    # User fields.
    name = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(16), nullable=True)

    # The quizzes created by this user.
    db_quizzes = db.relationship('DBQuiz', backref='user', lazy=True)

    # The answers of this user on quizzes.
    db_answers = db.relationship('DBUserAnswer', backref='user', lazy=True)

    def get_quizzes(self):
        """ Get the normal quiz objects that this user has created. """
        return [db_quiz.get_quiz() for db_quiz in self.db_quizzes]

    def get_latest_answer_sets(self):
        """
        Get the latest answer sets this user has entered for each quiz they've taken.
        """
        # Group all of the answer sets by the quizzes they belong to.
        answer_sets_by_quiz = {}
        for answer_set in self.get_answer_sets():
            quiz_id = answer_set.quiz.get_db_quiz().id
            if answer_set.quiz in answer_sets_by_quiz:
                answer_sets_by_quiz[quiz_id].append(answer_set)
            else:
                answer_sets_by_quiz[quiz_id] = [answer_set]

        # Get the latest answer set from each quiz.
        latest_answer_sets = []
        for answer_set_list in answer_sets_by_quiz.values():
            # Find the answer set with the highest representative ID.
            latest_answer_set = None
            latest_answer_set_id = None
            for answer_set in answer_set_list:
                answer_set_id = answer_set.get_representative_id()
                if answer_set_id is None:
                    continue
                if latest_answer_set is None or answer_set_id > latest_answer_set_id:
                    latest_answer_set = answer_set
                    latest_answer_set_id = answer_set_id

            # Append the highest ID answer set to the list.
            if latest_answer_set is not None:
                latest_answer_sets.append(latest_answer_set)
        return latest_answer_sets

    def get_answer_sets(self):
        """
        Get the answer sets to all the quizzes this user has taken.
        """
        # Get all of the answer objects, and group them by uuid.
        answers_by_uuid = {}
        for db_answer in self.db_answers:
            answer = db_answer.get_user_answer(self)
            # Edge case when editing a quiz of old.
            if answer.question is None:
                continue

            if answer.uuid in answers_by_uuid:
                answers_by_uuid[answer.uuid].append(answer)
            else:
                answers_by_uuid[answer.uuid] = [answer]

        # Convert these into answer sets.
        answer_sets = []
        for uuid, answers in answers_by_uuid.items():
            # Find the ID of the quiz that these answers are for.
            quiz_id = None
            for answer in answers:
                answer_quiz_id = answer.question.get_db_question().quiz_id
                if quiz_id is None:
                    quiz_id = answer_quiz_id
                elif quiz_id != answer_quiz_id:
                    # Skip this answer set as it is inconsistent.
                    quiz_id = None
                    break

            # If no unanimous quiz ID could be found, skip it.
            if quiz_id is None:
                continue

            # Load the quiz, and create the answer set.
            quiz = load_quiz(quiz_id)
            answer_set = AnswerSet(quiz, uuid, answers)
            answer_sets.append(answer_set)

        # Return the answer sets that were found.
        return answer_sets


class DBUserAnswer(db.Model):
    """ The answer of a user to a quiz. """
    # The internal key assigned for each user answer.
    id = db.Column(db.Integer, primary_key=True, nullable=False)

    # The unique UUID that groups the answers to each taking of a quiz.
    uuid = db.Column(db.String(36), nullable=False)

    # The ID of the user that entered this answer.
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    # The ID of the parent question to this answer.
    question_id = db.Column(db.Integer, db.ForeignKey('quiz_question.id'), nullable=False)

    # The answer the user entered.
    answer = db.Column(db.Float, nullable=False)

    def get_user_answer(self, user=None, question=None):
        """ Get the normal user answer object associated with this db user answer. """
        if user is None:
            user = load_user(self.user_id)
        if question is None:
            question = load_question(self.question_id)
        answer = UserAnswer(self.uuid, user, question, self.answer)
        answer.set_db_answer(self)
        return answer
