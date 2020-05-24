"""
Manages the database model that holds quizzes and their questions.
"""

from . import db
from .quiz import Quiz, Category
from .question import AnswerSpec, Question
from .scoring_function import ScoringFunction


def load_quiz(quiz_id):
    """ Loads the quiz with the given quiz ID. """
    db_quiz = DBQuiz.query.get(int(quiz_id))
    return db_quiz.get_quiz() if db_quiz is not None else None


def load_all_quizzes():
    """ Loads all of the quizzes. """
    db_quizzes = DBQuiz.query.all()
    return [db_quiz.get_quiz() for db_quiz in db_quizzes]


def load_question(question_id):
    """ Loads the quiz question associated with the given question ID. """
    question = DBQuizQuestion.query.get(int(question_id))
    return question.get_question() if question is not None else None


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
    quiz.set_db_quiz(db_quiz)
    db.session.add(db_quiz)
    db.session.commit()

    # Add all of the contents of the quiz to the database.
    update_quiz_in_db(None, quiz)
    return errors


def edit_db_quiz(old_quiz, new_quiz):
    """ Edits a quiz in the database. """
    errors = check_quiz(new_quiz)
    if len(errors) > 0:
        return errors

    # Update the contents of the quiz in the database.
    update_quiz_in_db(old_quiz, new_quiz)
    return errors


def delete_db_quiz(quiz):
    """
    Deletes a quiz from the database.
    CAUTION: This is not reversible.
    """
    errors = []

    # Update the quiz to nothing to remove it.
    update_quiz_in_db(quiz, None)

    # Delete the quiz itself.
    db.session.delete(quiz.get_db_quiz())
    db.session.commit()
    return errors


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


def diff_quiz_questions(old_quiz, new_quiz):
    """
    Determines the questions that were added and removed from each quiz.
    Note: If a question is changed, it is treated as though
          that question was removed and then added again.

    Also updates the references of matching questions in the old and new
    quizzes so that they point to the same db question.
    """
    # If there is no old quiz, then all the questions must be added.
    if old_quiz is None:
        return new_quiz.questions, []
    # If there is no new quiz, then all the questions should be removed.
    if new_quiz is None:
        return [], old_quiz.questions

    # Initialise these lists as all the questions that could
    # have been added or removed, and then narrow it down later.
    questions_to_add = new_quiz.questions.copy()
    questions_to_remove = old_quiz.questions.copy()

    # Any questions that exist in both new and old shouldn't be removed.
    for new_question in new_quiz.questions:
        old_question = Question.find(old_quiz.questions, new_question)
        if old_question is not None:
            new_question.set_db_question(old_question.get_db_question())
            questions_to_remove.remove(old_question)

    # Any questions that exist in both new and old shouldn't be added.
    for old_question in old_quiz.questions:
        new_question = Question.find(new_quiz.questions, old_question)
        if old_question in questions_to_add:
            new_question.set_db_question(old_question.get_db_question())
            questions_to_add.remove(old_question)

    # Return the lists of questions added and removed.
    return questions_to_add, questions_to_remove


def diff_quiz_categories(old_quiz, new_quiz):
    """
    Determines the categories that were added and removed from each quiz.
    Note: If a category name is changed, it is treated as though
          that category was removed and then added again.

    Also updates the references of matching categories in the old and new
    quizzes so that they point to the same db category.
    """
    # If there is no old quiz, then all the categories must be added.
    if old_quiz is None:
        return new_quiz.categories, []
    # If there is no new quiz, then all the categories should be removed.
    if new_quiz is None:
        return [], old_quiz.categories

    # Initialise these lists as all the categories that could
    # have been added or removed, and then narrow it down later.
    categories_to_add = new_quiz.categories.copy()
    categories_to_remove = old_quiz.categories.copy()

    # Any categories that exist in both new and old shouldn't be removed.
    for new_category in new_quiz.categories:
        old_category = Category.find_by_name(categories_to_remove, new_category.name)
        if old_category is not None:
            new_category.set_db_category(old_category.get_db_category())
            categories_to_remove.remove(old_category)

    # Any categories that exist in both new and old shouldn't be added.
    for old_category in old_quiz.categories:
        new_category = Category.find_by_name(categories_to_add, old_category.name)
        if new_category is not None:
            new_category.set_db_category(old_category.get_db_category())
            categories_to_add.remove(new_category)

    # Return the lists of questions added and removed.
    return categories_to_add, categories_to_remove


def update_quiz_questions_in_db(db_quiz, old_quiz, new_quiz):
    """ Updates the questions of db_quiz represented by old_quiz to the questions in new_quiz. """
    # Find the questions that changed.
    questions_to_add, questions_to_remove = diff_quiz_questions(old_quiz, new_quiz)

    # Remove all of the old questions.
    for question in questions_to_remove:
        # Delete the answer specs dependent on this question.
        for category in old_quiz.categories:
            for answer_spec in category.answer_specs:
                if question == answer_spec.question:
                    db.session.delete(answer_spec.get_db_answer_spec())

        # Delete the user answers dependent on this question.
        from .user_model import DBUserAnswer
        answers_to_delete = DBUserAnswer.query.filter_by(question_id=question.get_db_question().id).all()
        for answer_to_delete in answers_to_delete:
            db.session.delete(answer_to_delete)

        # Delete the question itself.
        db.session.delete(question.get_db_question())

    # Add all of the new questions.
    for question in questions_to_add:
        db_question = DBQuizQuestion(
            quiz_id=db_quiz.id,
            index=-1,
            text=question.text,
            encoded_question=question.encode()
        )
        question.set_db_question(db_question)
        db.session.add(db_question)

    if new_quiz is not None:
        # Update the order index for each question.
        for index, question in enumerate(new_quiz.questions):
            question.get_db_question().index = index


def update_quiz_category_answer_specs_in_db(old_category, new_category):
    """ Updates the answer specs stored in the db. """
    # Remove all of the old answer specs.
    if old_category is not None:
        for answer_spec in old_category.answer_specs:
            db.session.delete(answer_spec.get_db_answer_spec())

    # Add all of the new answer specs.
    if new_category is not None:
        for answer_spec in new_category.answer_specs:
            # Get the db question associated with this answer spec.
            db_question = answer_spec.question.get_db_question()

            # Create the new answer spec in the database.
            db_answer_spec = DBQuizCategoryAnswerSpec(
                category_id=new_category.get_db_category().id,
                question_id=db_question.id,
                encoded_spec=answer_spec.scoring_function.encode()
            )
            answer_spec.set_db_answer_spec(db_answer_spec)
            db.session.add(db_answer_spec)


def update_quiz_categories_in_db(db_quiz, old_quiz, new_quiz):
    """ Updates the categories of db_quiz represented by old_quiz to the categories in new_quiz. """
    # Find the categories that have changed.
    categories_to_add, categories_to_remove = diff_quiz_categories(old_quiz, new_quiz)

    # Remove all of the old categories.
    for category in categories_to_remove:
        for answer_spec in category.answer_specs:
            db.session.delete(answer_spec.get_db_answer_spec())
        db.session.delete(category.get_db_category())

    # Add all the new categories of the quiz to the database.
    for category in categories_to_add:
        db_category = DBQuizCategory(
            quiz_id=db_quiz.id,
            name=category.name
        )
        category.set_db_category(db_category)
        db.session.add(db_category)

    # Commit the added questions and categories.
    db.session.commit()

    # Update the answer specs for all of the categories.
    if new_quiz is not None:
        for new_category in new_quiz.categories:
            # Find the old category that changed into this new category.
            if old_quiz is not None:
                old_category = Category.find_by_name(old_quiz.categories, new_category.name)
            else:
                old_category = None

            # Update all of the answer specs of the category.
            update_quiz_category_answer_specs_in_db(old_category, new_category)


def update_quiz_in_db(old_quiz, new_quiz):
    """ Populates a quiz with the given categories and questions. """
    # Get the db quiz we are editing.
    db_quiz = (old_quiz if old_quiz is not None else new_quiz).get_db_quiz()

    if new_quiz is not None:
        # Update the db quiz associated with the new quiz.
        new_quiz.set_db_quiz(db_quiz)
        # Make sure the ID of the quiz object is up to date with the ID in the database.
        new_quiz.id = db_quiz.id
        # Make sure the title of the quiz is up to date with the title of the quiz in the database.
        db_quiz.name = new_quiz.name

    # Update the questions in the database.
    update_quiz_questions_in_db(db_quiz, old_quiz, new_quiz)

    # Update the categories in the database.
    update_quiz_categories_in_db(db_quiz, old_quiz, new_quiz)

    # Commit all of the changes we made.
    db.session.commit()


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
        from .user_model import load_user
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

        # Create the quiz object.
        quiz = Quiz(self.id, self.name, owner, questions, categories)
        quiz.set_db_quiz(self)
        return quiz


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
        question = Question.parse(self.text, self.encoded_question)
        question.set_db_question(self)
        return question


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

        # Create the category object.
        category = Category(self.name, answer_specs)
        category.set_db_category(self)
        return category


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
        # Parse the scoring function associated with this answer spec.
        scoring_function = ScoringFunction.parse(self.encoded_spec)

        # Create the answer spec.
        answer_spec = AnswerSpec(question, scoring_function)
        answer_spec.set_db_answer_spec(self)
        return answer_spec
