#
# This file manages the database for storing quizzes.
#

import csv
from io import StringIO
from . import db

class Quiz(db.Model):
    """ The database entry for each quiz available on the site. """
    __tablename__ = 'quizzes'

    # The internal key assigned for each user.
    id = db.Column(db.Integer, primary_key=True, nullable=False)

    # Metadata about the quiz.
    name = db.Column(db.String(128), nullable=False)


class QuizQuestion(db.Model):
    """ The database entry for each question within a quiz. """
    __tablename__ = 'quiz_questions'

    # The internal key assigned for each user.
    id = db.Column(db.Integer, primary_key=True, nullable=False)

    # Used to sort the questions in the quiz.
    index = db.Column(db.Integer, nullable=False)

    # The text of the question.
    text = db.Column(db.String(512), nullable=False)

    # A string specifying the question type and the possible answers.
    encoded_question = db.Column(db.String(4096), nullable=False)

    def get_question():
        """ Return the parsed question object. """
        return parse_question(self.text, self.encoded_question)

    def set_question(question):
        """ Sets the question content for this object. """
        self.text = question.text
        self.encoded_question = question.encode()



def parse_question(text, encoded_question):
    """
    Decodes the underlying question into an object.

    Questions are encoded in the format:
        type(arg1, arg2, ..., argN)
    """
    try:
        opening_bracket = encoded_question.index("(")
    except ValueError:
        return MalformedQuestion(text, "Missing opening bracket")

    try:
        closing_bracket = encoded_question.rindex(")")
    except ValueError:
        return MalformedQuestion(text, "Missing closing bracket")

    # Extract the type and the arguments as strings from the encoded question.
    type = encoded_question[:opening_bracket]
    args_str = encoded_question[opening_bracket + 1 : closing_bracket]

    # Decode the arguments list in the CSV format.
    args = list(csv.reader([args_str]))[0]

    # Check if we recognise the type.
    if type == "multi":
        return parse_multi_question(text, args)
    if type == "slider":
        return parse_slider_question(text, args)

    # Otherwise, return an errored question.
    return MalformedQuestion(text, "Unknown question type \"" + type + "\" for encoded question: " + encoded_question)

class Question:
    """ A question in a quiz. """

    def __init__(self, type, text, is_valid):
        # The type of the question.
        self.type = type

        # The text of the question.
        self.text = text

        # Whether the question can be displayed to the user.
        self.is_valid = is_valid

    def encode(self):
        """ Encode this question into a string to store in the database. """

        # Encoding invalid questions is unsupported.
        if not self.is_valid:
            raise Exception("Encoding invalid questions is unsupported")

        # Encode the question's parameters into a list of arguments.
        args = self.encode_to_args()

        # Encode the arguments into a CSV string.
        args_str_io = StringIO()
        csv.writer(args_str_io).writerow(args)
        args_str = args_str_io.getvalue().strip()
        args_str_io.close()

        # Combine the type of this question and the CSV encoded arguments into one string.
        return self.type + "(" + args_str + ")"

    def encode_to_args(self):
        """ Encodes this question into a list of arguments. """
        raise NotImplementedError

    def __eq__(self, other):
        """ Check that this question is identical to other. """
        return self.type == other.type and self.text == other.text and self.is_valid == other.is_valid

    def __str__(self):
        """ Return the question as a string. """
        type = self.type
        text = self.text
        valid = str(self.is_valid)
        encoded = self.encode()
        return "Question{type: " + type + ", text: " + text + ", valid: " + valid + ", encoded: " + encoded + "}"

    def __repr__(self):
        """ Return the question as a string. """
        return str(self)



class MalformedQuestion(Question):
    """ A question that cannot be parsed. """

    def __init__(self, text, error):
        # Initialise the super class.
        Question.__init__(self, "malformed", text, False)

        # The error for why the question could not be parsed.
        self.error = error

    def __eq__(self, other):
        """ Check that this question is identical to other. """
        return super().__eq__(other) and self.error == other.error



def parse_multi_question(text, args):
    """
    Parses a multi-choice question.

    Format:
        multi(choice1, choice2, ..., choiceN)
    """
    return MultiChoiceQuestion(text, args)

class MultiChoiceQuestion(Question):
    """ A question that cannot be parsed. """

    def __init__(self, text, options):
        # Initialise the super class.
        Question.__init__(self, "multi", text, True)

        # The possible choices.
        self.options = options

    def encode_to_args(self):
        """ Encodes this question into a list of arguments. """
        return self.options

    def __eq__(self, other):
        """ Check that this question is identical to other. """
        return super().__eq__(other) and self.options == other.options



def parse_slider_question(text, args):
    """
    Parses a slider question.

    Format:
        slider(min, max)
    """

    # Make sure there are the expected number of arguments.
    if len(args) != 2:
        return MalformedQuestion(text, "Expected two arguments, got: " + str(len(args)))

    # Parse the min possible value.
    try:
        min = float(args[0])
    except ValueError:
        return MalformedQuestion(text, "Expected min to be a number, instead was: " + args[0])

    # Parse the max possible value.
    try:
        max = float(args[1])
    except ValueError:
        return MalformedQuestion(text, "Expected max to be a number, instead was: " + args[1])

    return SliderQuestion(text, min, max)

class SliderQuestion(Question):
    """ A question that takes a slider value. """

    def __init__(self, text, min, max):
        # Initialise the super class.
        Question.__init__(self, "slider", text, True)

        # The minimum possible value that can be chosen.
        self.min = min

        # The maximum possible value that can be chosen.
        self.max = max

    def encode_to_args(self):
        """ Encodes this question into a list of arguments. """
        return [self.min, self.max]

    def __eq__(self, other):
        """ Check that this question is identical to other. """
        return super().__eq__(other) and self.min == other.min and self.max == other.max
