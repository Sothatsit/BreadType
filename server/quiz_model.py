"""
Manages the database model that holds quizzes and their questions.
"""

from . import db
from .question_types import Question
from .user_model import load_user


def load_quiz(quiz_id):
    """ Loads the quiz with the given quiz ID. """
    return Quiz.query.get(int(quiz_id))


def load_all_quizzes():
    """ Loads all of the quizzes. """
    return Quiz.query.all()


def populate_quiz_in_db(quiz, questions):
    """ Populates a quiz with the given questions. """
    # Add all the questions of the quiz to the database.
    for index, question in enumerate(questions):
        if not question.is_valid:
            continue

        db_question = QuizQuestion(
            quiz_id=quiz.id,
            index=index,
            text=question.text,
            encoded_question=question.encode()
        )
        db.session.add(db_question)

    # Commit all the changes.
    db.session.commit()


def create_db_quiz(owner, title, questions):
    """ Creates a quiz in the database. """

    # Create the quiz and add it to the database.
    quiz = Quiz(
        owner=owner,
        name=title
    )
    db.session.add(quiz)
    db.session.commit()

    # Add the questions to the database.
    populate_quiz_in_db(quiz, questions)
    return quiz


def edit_db_quiz(quiz, title, questions):
    """ Edits a quiz in the database. """

    # Update the title of the quiz.
    quiz.title = title

    # Remove all of the old questions from the quiz.
    for question in quiz.encoded_questions:
        db.session.delete(question)

    # Add the questions to the database.
    populate_quiz_in_db(quiz, questions)
    return quiz


class Quiz(db.Model):
    """ The database entry for each quiz available on the site. """
    __tablename__ = 'quiz'

    # The internal key assigned for each user.
    id = db.Column(db.Integer, primary_key=True, nullable=False)

    # The ID of the user that created this quiz.
    owner = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    # Metadata about the quiz.
    name = db.Column(db.String(128), nullable=False)

    # The questions within this quiz.
    encoded_questions = db.relationship('QuizQuestion', backref='quiz', lazy=False)

    def load_owner_user(self):
        """ Loads the User object for the owner of this quiz. """
        return load_user(self.owner)

    def get_questions(self):
        """ Returns a list of all the parsed question objects. """
        ordered_questions = sorted(self.encoded_questions, key=lambda q: q.index)
        return [entry.get_question() for entry in ordered_questions]

    def get_questions_text(self):
        """ Returns text that represents all the questions in this quiz. """
        questions_text = ""
        for question in self.get_questions():
            questions_text += question.text + "\n"
            questions_text += question.encode() + "\n"
            questions_text += "\n"
        return questions_text


class QuizQuestion(db.Model):
    """ The database entry for each question within a quiz. """
    __tablename__ = 'quiz_question'

    # The internal key assigned for each user.
    id = db.Column(db.Integer, primary_key=True, nullable=False)

    # The key of the parent quiz to this question.
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id'), nullable=False)

    # Used to sort the questions in the quiz.
    index = db.Column(db.Integer, nullable=False)

    # The text of the question.
    text = db.Column(db.String(512), nullable=False)

    # A string specifying the question type and the possible answers.
    encoded_question = db.Column(db.String(4096), nullable=False)

    def set_question(self, question):
        """ Sets the question content for this object. """
        self.text = question.text
        self.encoded_question = question.encode()

    def get_question(self):
        """ Returns the parsed question that this db question represents. """
        return Question.parse(self.text, self.encoded_question)
