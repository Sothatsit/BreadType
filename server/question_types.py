"""
Holds the server classes for representing different types of questions,
their encoding/decoding from strings, and their formatting as HTML.
"""

import csv
from io import StringIO


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

    def write_html(self, index):
        """ Write this question as HTML. """
        raise NotImplementedError

    def get_answer_from_form(self, form, index):
        """ Get the answer that was given for this question from the form. """
        return form.get("question-{}".format(index))

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

    @staticmethod
    def parse(text, encoded_question):
        """ Parses the given encoded question into a Question object. """
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
            return MultiChoiceQuestion.parse(text, args)
        if type == "float_slider":
            return FloatSliderQuestion.parse(text, args)
        if type == "int_slider":
            return IntSliderQuestion.parse(text, args)

        # Otherwise, return an errored question.
        return MalformedQuestion(
            text, "Unknown question type \"" + type + "\" for encoded question: " + encoded_question
        )

    @staticmethod
    def parse_many(text_questions):
        """
        Parses a multi-line set of questions.

        Format:
          text1
          question1

          text2
          question2

          ...

          textN
          questionN

        Note:
          Blank lines and lines starting with # are ignored
        """
        text = None
        questions = []

        # Split the text into lines to parse.
        for line in text_questions.splitlines():
            line = line.strip()

            # Skip empty or comment lines.
            if len(line) == 0 or line[0] == "#":
                continue

            # This line is the text for a question.
            if text is None:
                text = line
                continue

            # Parse the question.
            questions.append(Question.parse(text, line))

            # Mark that the next line is text.
            text = None

        return questions


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


class MultiChoiceQuestion(Question):
    """ A question that has a few distinct answers. """

    def __init__(self, text, options):
        # Initialise the super class.
        Question.__init__(self, "multi", text, True)

        # The possible choices.
        self.options = options

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
            html += "<input type=\"radio\" id=\"q{}-o{}\" name=\"question-{}\" value=\"option-{}\">\n".format(
                index, option_index, index, option_index
            )
            html += "<label for=\"option-{}\">{}</label>\n".format(option_index, option)
            html += "</div>\n"

        html += "</div>"
        return html

    def __eq__(self, other):
        """ Check that this question is identical to other. """
        return super().__eq__(other) and self.options == other.options

    @staticmethod
    def parse(text, args):
        """
        Parses a multi-choice question.

        Format:
            multi(choice1, choice2, ..., choiceN)
        """
        return MultiChoiceQuestion(text, args)


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

    def encode_to_args(self):
        """ Encodes this question into a list of arguments. """
        return [self.min, self.max]

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
