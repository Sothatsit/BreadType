"""
Manages the database model that holds quizzes and their questions.
"""

from . import db
from .quiz import Quiz, Category
from .question import AnswerSpec, Question
from .scoring_function import ScoringFunction
from .user_model import load_user


def load_quiz(quiz_id):
    """ Loads the quiz with the given quiz ID. """
    db_quiz = DBQuiz.query.get(int(quiz_id))
    return db_quiz.get_quiz() if db_quiz is not None else None


def load_all_quizzes():
    """ Loads all of the quizzes. """
    db_quizzes = DBQuiz.query.all()
    return [db_quiz.get_quiz() for db_quiz in db_quizzes]


def populate_quiz_in_db(db_quiz, quiz):
    """ Populates a quiz with the given categories and questions. """
    # Update the ID of the quiz object to the ID in the database.
    quiz.id = db_quiz.id

    # Add all the questions of the quiz to the database.
    db_questions = {}
    for index, question in enumerate(quiz.questions):
        if not question.is_valid:
            continue

        db_question = DBQuizQuestion(
            quiz_id=db_quiz.id,
            index=index,
            text=question.text,
            encoded_question=question.encode()
        )
        db_questions[question] = db_question
        db.session.add(db_question)

    # Add all the categories of the quiz to the database.
    db_categories = {}
    for category in quiz.categories:
        db_category = DBQuizCategory(
            quiz_id=db_quiz.id,
            name=category.name
        )
        db_categories[category] = db_category
        db.session.add(db_category)

    # Commit the added questions and categories.
    db.session.commit()

    # Add all the answer specs.
    for category in quiz.categories:
        db_category = db_categories[category]

        for answer_spec in category.answer_specs:
            if answer_spec.question not in db_questions:
                continue
            db_question = db_questions[answer_spec.question]

            db_answer_spec = DBQuizCategoryAnswerSpec(
                category_id=db_category.id,
                question_id=db_question.id,
                encoded_spec=answer_spec.encoded
            )
            db.session.add(db_answer_spec)

    # Commit the added category answer specs.
    db.session.commit()


def check_quiz(quiz):
    """ Checks a quiz for errors. """
    errors = []
    if len(quiz.name) == 0:
        errors.append("Please enter a title.")
    if len(quiz.questions) == 0:
        errors.append("Please enter some questions.")
    for index, question in enumerate(quiz.questions):
        if question.is_valid:
            continue
        errors.append("Could not parse question {}: {}".format(index, question.error))
    return errors


def create_db_quiz(quiz):
    """ Creates a quiz in the database. """
    errors = check_quiz(quiz)
    if len(errors) > 0:
        return errors

    # Create the quiz and add it to the database.
    db_quiz = DBQuiz(
        owner=quiz.owner.id,
        name=quiz.name
    )
    db.session.add(db_quiz)
    db.session.commit()

    # Add all of the contents of the quiz to the database.
    populate_quiz_in_db(db_quiz, quiz)
    return errors


def edit_db_quiz(old_quiz, new_quiz):
    """ Edits a quiz in the database. """
    errors = check_quiz(new_quiz)
    if len(errors) > 0:
        return errors

    # Load the db quiz to be edited.
    db_quiz = DBQuiz.query.get(int(old_quiz.id))

    # Update the title of the quiz.
    db_quiz.name = new_quiz.name

    # Remove all of the old questions from the quiz.
    for question in db_quiz.db_questions:
        db.session.delete(question)

    # Remove all of the old categories from the quiz.
    for category in db_quiz.db_categories:
        for answer_spec in category.db_answer_specs:
            db.session.delete(answer_spec)
        db.session.delete(category)

    # Add all of the contents of the quiz to the database.
    populate_quiz_in_db(db_quiz, new_quiz)
    return errors


class DBQuiz(db.Model):
    """ The database entry for each quiz available on the site. """
    __tablename__ = 'quiz'

    # The internal key assigned for each user.
    id = db.Column(db.Integer, primary_key=True, nullable=False)

    # The ID of the user that created this quiz.
    owner = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    # The name of the quiz.
    name = db.Column(db.String(128), nullable=False)

    # The questions within this quiz.
    db_questions = db.relationship('DBQuizQuestion', backref='quiz', lazy=False)

    # The categories within this quiz.
    db_categories = db.relationship('DBQuizCategory', backref='quiz', lazy=False)

    def get_quiz(self):
        """ Returns a quiz object representing this quiz. """
        # Load the user that owns this quiz.
        owner = load_user(self.owner)

        # We want the questions to be ordered as the quiz creator specified.
        ordered_db_questions = sorted(self.db_questions, key=lambda q: q.index)

        # Convert the db questions to normal questions.
        questions = []
        questions_by_id = {}
        for db_question in ordered_db_questions:
            question = db_question.get_question()
            questions.append(question)
            questions_by_id[db_question.id] = question

        # Convert the db categories to normal categories.
        categories = []
        for db_category in self.db_categories:
            categories.append(db_category.get_category(questions_by_id))

        return Quiz(self.id, self.name, owner, questions, categories)


class DBQuizQuestion(db.Model):
    """ The database entry for each question within a quiz. """
    __tablename__ = 'quiz_question'

    # The internal key assigned for each user.
    id = db.Column(db.Integer, primary_key=True, nullable=False)

    # The ID of the parent quiz to this question.
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id'), nullable=False)

    # Used to sort the questions in the quiz.
    index = db.Column(db.Integer, nullable=False)

    # The text of the question.
    text = db.Column(db.String(512), nullable=False)

    # A string specifying the question type and the possible answers.
    encoded_question = db.Column(db.String(4096), nullable=False)

    # The answers for this question.
    db_answers = db.relationship('DBQuizCategoryAnswerSpec', backref='question', lazy=False)

    def get_question(self):
        """ Returns the parsed question that this db question represents. """
        return Question.parse(self.text, self.encoded_question)


class DBQuizCategory(db.Model):
    """ The database entry for each category that a user could be placed in from their answers to a quiz. """
    __tablename__ = "quiz_category"

    # The internal key assigned for each category.
    id = db.Column(db.Integer, primary_key=True, nullable=False)

    # The ID of the parent quiz to this category.
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id'), nullable=False)

    # The name of the category.
    name = db.Column(db.String(128), nullable=False)

    # The answers for this category.
    db_answer_specs = db.relationship('DBQuizCategoryAnswerSpec', backref='category', lazy=False)

    def get_category(self, questions_by_id):
        """ Returns the parsed category that this db category represents. """
        # Convert the db answer specs into normal answer specs.
        answer_specs = []
        for db_answer_spec in self.db_answer_specs:
            question = questions_by_id[db_answer_spec.question_id]
            answer_spec = db_answer_spec.get_answer_spec(question)
            answer_specs.append(answer_spec)
        return Category(self.name, answer_specs)


class DBQuizCategoryAnswerSpec(db.Model):
    """
    The specification for how to rate a user's answer to a question.
    This is used to determine the category of a user based on their answers.
    """
    __tablename__ = "quiz_category_answer_spec"

    # The internal key assigned for each category answer.
    id = db.Column(db.Integer, primary_key=True, nullable=False)

    # The ID of the parent quiz category to this answer.
    category_id = db.Column(db.Integer, db.ForeignKey('quiz_category.id'), nullable=False)

    # The ID of the parent question to this answer.
    question_id = db.Column(db.Integer, db.ForeignKey('quiz_question.id'), nullable=False)

    # The specification for this answer. Its format is dependent on the question.
    encoded_spec = db.Column(db.String(4096), nullable=False)

    def get_answer_spec(self, question):
        """ Returns the parsed answer spec that this db answer spec represents. """
        scoring_function = ScoringFunction.parse(self.encoded_spec)
        return AnswerSpec(question, scoring_function)
