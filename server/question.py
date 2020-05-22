"""
Holds the server classes for representing different types of questions,
their encoding/decoding from strings, and their formatting as HTML.
"""

from .encoding import parse_function, encode_function
from .scoring_function import ScoringFunction


class AnswerSpec:
    """ The specification for scoring an answer to a question. """

    def __init__(self, question, scoring_function):
        self.question = question
        self.scoring_function = scoring_function

    def __hash__(self):
        """ Hashes this answer spec so it can be used in dictionaries. """
        return hash(id(self))


class Question:
    """ A question in a quiz. """

    def __init__(self, question_type, text, is_valid):
        # The type of the question.
        self.question_type = question_type

        # The text of the question.
        self.text = text

        # Whether the question can be displayed to the user.
        self.is_valid = is_valid

    def encode(self):
        """ Encode this question into a string to store in the database. """
        # Encoding invalid questions is unsupported.
        if not self.is_valid:
            raise Exception("Encoding invalid questions is unsupported")

        # Encode the question type into "question_type(args)"
        return encode_function(self.question_type, self.encode_to_args())

    def encode_to_args(self):
        """ Encodes this question into a list of arguments. """
        raise NotImplementedError

    def write_html(self, index):
        """ Write this question as HTML. """
        raise NotImplementedError

    def get_answer_from_form(self, form, index):
        """ Get the answer that was given for this question from the form. """
        text_answer = form.get("question-{}".format(index), "").strip()
        return text_answer if len(text_answer) > 0 else None

    def score_answer(self, answer, answer_spec):
        """ Give a score to the answer based on the given answer spec. """
        raise NotImplementedError

    def __eq__(self, other):
        """ Check that this question is identical to other. """
        return self.question_type == other.question_type and self.text == other.text and self.is_valid == other.is_valid

    def __hash__(self):
        """ Hashes this question so it can be used in dictionaries. """
        return hash("type: " + self.question_type + ", text: " + self.text + ", is_valid: " + str(self.is_valid))

    def __str__(self):
        """ Return the question as a string. """
        q_type = self.question_type
        text = self.text
        valid = str(self.is_valid)
        encoded = self.encode()
        return "Question{type: " + q_type + ", text: " + text + ", valid: " + valid + ", encoded: " + encoded + "}"

    def __repr__(self):
        """ Return the question as a string. """
        return str(self)

    @staticmethod
    def parse(text, encoded_question):
        """ Parses the given encoded question into a Question object. """
        # Extract the question type and arguments from the encoded question.
        try:
            question_type, args = parse_function(encoded_question)
        except ValueError as e:
            return MalformedQuestion(text, str(e))

        # Check if we recognise the type.
        if question_type == "multi":
            return MultiChoiceQuestion.parse(text, args)
        if question_type == "float_slider":
            return FloatSliderQuestion.parse(text, args)
        if question_type == "int_slider":
            return IntSliderQuestion.parse(text, args)

        # Otherwise, return an errored question.
        return MalformedQuestion(
            text, "Unknown question type \"" + question_type + "\" for encoded question: " + encoded_question
        )


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

    def __hash__(self):
        """ Hashes this question so it can be used in dictionaries. """
        parent_hash = super(MalformedQuestion, self).__hash__()
        return hash(str(parent_hash) + ", " + self.error)


class MultiChoiceQuestion(Question):
    """ A question that has a few distinct answers. """

    def __init__(self, text, options):
        # Initialise the super class.
        Question.__init__(self, "multi", text, True)

        # The possible choices.
        self.options = options

    def get_answer_from_form(self, form, index):
        """ Get the answer that was given for this question from the form. """
        text_answer = super(MultiChoiceQuestion, self).get_answer_from_form(form, index)
        if text_answer is None:
            return None
        return int(text_answer)

    def encode_to_args(self):
        """ Encodes this question into a list of arguments. """
        return self.options

    def write_html(self, index):
        """ Write this question as HTML. """
        html = "<div class=\"multi-choice\">\n"

        for option_index, option in enumerate(self.options):
            # Javascript that selects this choice.
            select_js = "document.getElementById(&quot;q{}-o{}&quot;).checked=true".format(index, option_index)

            # Each choice is held within its own div.
            html += "<div class=\"choice\" onclick=\"{}\">\n".format(select_js)
            html += "<input type=\"radio\" id=\"q{}-o{}\" name=\"question-{}\" value=\"{}\">\n".format(
                index, option_index, index, option_index + 1
            )
            html += "<label for=\"option-{}\">{}</label>\n".format(option_index, option)
            html += "</div>\n"

        html += "</div>"
        return html

    def __eq__(self, other):
        """ Check that this question is identical to other. """
        return super().__eq__(other) and self.options == other.options

    def __hash__(self):
        """ Hashes this question so it can be used in dictionaries. """
        return super(MultiChoiceQuestion, self).__hash__()

    @staticmethod
    def parse(text, args):
        """
        Parses a multi-choice question.

        Format:
            multi(choice1, choice2, ..., choiceN)
        """
        return MultiChoiceQuestion(text, args)

    @staticmethod
    def from_form(question_number, text, form, errors):
        """
        Parses a multi-choice question from the given form.
        """
        # Get all of the choices out of the form.
        options = []
        option_number = 0
        while "question_{}_multi_choice_{}".format(question_number, option_number + 1) in form:
            option = form.get("question_{}_multi_choice_{}".format(question_number, option_number + 1), "")
            option_number += 1

            print("option {}".format(option_number))

            if len(option) == 0:
                errors.append("Missing text for option {} of multi-choice question {}".format(
                    option_number, question_number
                ))
                continue

            options.append(option)

        # Create the multi-choice question.
        return MultiChoiceQuestion(text, options)


def create_slider_input_html(min_value, max_value, step, default_value, name):
    """"
    :return: the HTML for a slider with the given parameters.
    """
    html = "<input class=\"sliders\" type=\"range\" "
    html += "min=\"{}\" max=\"{}\" step=\"{}\"".format(min_value, max_value, step)
    html += "value=\"{}\" name=\"{}\"".format(default_value, name)
    html += " \\>"
    return html


class FloatSliderQuestion(Question):
    """ A question that takes a slider value. """

    def __init__(self, text, min_value, max_value):
        # Initialise the super class.
        Question.__init__(self, "float_slider", text, True)

        # The minimum possible value that can be chosen.
        self.min_value = float(min_value)

        # The maximum possible value that can be chosen.
        self.max_value = float(max_value)

        # The default value for the slider.
        self.default_value = (min_value + max_value) / 2

        # The step between each value. HTML doesn't allow non-discrete sliders, but this is close enough.
        self.step = (max_value - min_value) / 1000000

    def get_answer_from_form(self, form, index):
        """ Get the answer that was given for this question from the form. """
        text_answer = super(FloatSliderQuestion, self).get_answer_from_form(form, index)
        if text_answer is None:
            return None
        return float(text_answer)

    def encode_to_args(self):
        """ Encodes this question into a list of arguments. """
        return [self.min_value, self.max_value]

    def write_html(self, index):
        """ Write this question as HTML. """
        html = "<div class=\"slider\">\n"
        html += create_slider_input_html(
            self.min_value, self.max_value, self.step, self.default_value, "question-{}".format(index)
        )
        html += "</div>"
        return html

    def __eq__(self, other):
        """ Check that this question is identical to other. """
        return super().__eq__(other) and self.min_value == other.min_value and self.max_value == other.max_value

    def __hash__(self):
        """ Hashes this question so it can be used in dictionaries. """
        return super(FloatSliderQuestion, self).__hash__()

    @staticmethod
    def parse(text, args):
        """
        Parses a slider question.

        Format:
            float_slider(min, max)
        """

        # Make sure there are the expected number of arguments.
        if len(args) != 2:
            return MalformedQuestion(text, "Expected two arguments, got: " + str(len(args)))

        # Parse the min possible value.
        try:
            min_value = float(args[0])
        except ValueError:
            return MalformedQuestion(text, "Expected min to be a number, instead was: " + args[0])

        # Parse the max possible value.
        try:
            max_value = float(args[1])
        except ValueError:
            return MalformedQuestion(text, "Expected max to be a number, instead was: " + args[1])

        return FloatSliderQuestion(text, min_value, max_value)

    @staticmethod
    def from_form(question_number, text, form, errors):
        """ Parse a continuous slider from the given form. """
        # Get the min and max from the form.
        min_text = form.get("question_{}_slider_min".format(question_number), "")
        max_text = form.get("question_{}_slider_max".format(question_number), "")
        if len(min_text) == 0 or len(max_text) == 0:
            errors.append("Missing min or max value for slider question {}".format(question_number))
            return None

        # Convert them to numbers.
        try:
            min_value = float(min_text)
            max_value = float(max_text)
        except ValueError:
            errors.append("Min and max must both be numbers for slider question {}".format(question_number))
            return None

        # Create the slider question.
        return FloatSliderQuestion(text, min_value, max_value)


class IntSliderQuestion(Question):
    """ A question that takes an integer slider value. """

    def __init__(self, text, min_value, max_value):
        # Initialise the super class.
        Question.__init__(self, "int_slider", text, True)

        # The minimum possible value that can be chosen.
        self.min_value = int(min_value)

        # The maximum possible value that can be chosen.
        self.max_value = int(max_value)

        # The default value for the slider.
        self.default_value = int((min_value + max_value) / 2)

    def get_answer_from_form(self, form, index):
        """ Get the answer that was given for this question from the form. """
        text_answer = super(IntSliderQuestion, self).get_answer_from_form(form, index)
        if text_answer is None:
            return None
        return int(text_answer)

    def write_html(self, index):
        """ Write this question as HTML. """
        html = "<div class=\"slider\">\n"
        html += create_slider_input_html(
            self.min_value, self.max_value, 1, self.default_value, "question-{}".format(index)
        )
        html += "</div>"
        return html

    def encode_to_args(self):
        """ Encodes this question into a list of arguments. """
        return [self.min_value, self.max_value]

    def __eq__(self, other):
        """ Check that this question is identical to other. """
        return super().__eq__(other) and self.min_value == other.min_value and self.max_value == other.max_value

    def __hash__(self):
        """ Hashes this question so it can be used in dictionaries. """
        return super(IntSliderQuestion, self).__hash__()

    @staticmethod
    def parse(text, args):
        """
        Parses a discrete slider question.

        Format:
            int_slider(min, max)
        """

        # Make sure there are the expected number of arguments.
        if len(args) != 2:
            return MalformedQuestion(text, "Expected two arguments, got: " + str(len(args)))

        # Parse the min possible value.
        try:
            min_value = int(args[0])
        except ValueError:
            return MalformedQuestion(text, "Expected min to be an integer, instead was: " + args[0])

        # Parse the max possible value.
        try:
            max_value = int(args[1])
        except ValueError:
            return MalformedQuestion(text, "Expected max to be an integer, instead was: " + args[1])

        return IntSliderQuestion(text, min_value, max_value)

    @staticmethod
    def from_form(question_number, text, form, errors):
        """ Parse a discrete slider from the given form. """
        # Get the min and max from the form.
        min_text = form.get("question_{}_slider_min".format(question_number), "")
        max_text = form.get("question_{}_slider_max".format(question_number), "")
        if len(min_text) == 0 or len(max_text) == 0:
            errors.append("Missing min or max value for slider question {}".format(question_number))
            return None

        # Convert them to numbers.
        try:
            min_value = int(min_text)
            max_value = int(max_text)
        except ValueError:
            errors.append("Min and max must both be integers for slider question {}".format(question_number))
            return None

        # Create the slider question.
        return IntSliderQuestion(text, min_value, max_value)
