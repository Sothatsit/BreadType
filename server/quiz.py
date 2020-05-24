"""
Holds the server classes for representing quizzes and their categories.
"""

import uuid
import datetime
from .question import Question, AnswerSpec, MultiChoiceQuestion, IntSliderQuestion, FloatSliderQuestion
from .scoring_function import ScoringFunction


class Quiz:
    """ A quiz held in memory. """

    def __init__(self, id, name, owner, questions, categories):
        self.id = id
        self.name = name
        self.owner = owner
        self.questions = questions
        self.categories = categories

        # For the templates cause they can't call enumerate.
        self.enumerated_questions = enumerate(questions)
        self.enumerated_categories = enumerate(categories)

        # The db quiz associated with this question.
        self.db_quiz = None

    def get_db_quiz(self):
        """ Get the db quiz associated with this quiz, or None. """
        return self.db_quiz

    def set_db_quiz(self, db_quiz):
        """ Set the db quiz associated with this quiz. """
        self.db_quiz = db_quiz

    def __hash__(self):
        """ Hashes this quiz so it can be used in dictionaries. """
        return hash(id(self))

    def encode(self):
        """ Encode this quiz into a text format that can be edited. """
        encoded = ""

        # The first section contains the category names.
        for category in self.categories:
            encoded += category.name + "\n"
        if len(self.categories) == 0:
            encoded += ":None\n"
        encoded += "\n"

        # The remaining sections contain the questions.
        for question in self.questions:
            encoded += question.text + "\n"
            encoded += question.encode() + "\n"
            for category in self.categories:
                answer_spec = category.get_answer_spec(question)
                if answer_spec is None:
                    raise RuntimeError("Missing answer spec for question in category " + category.name)
                encoded += answer_spec.scoring_function.encode() + "\n"
            encoded += "\n"

        return encoded

    @staticmethod
    def parse(quiz_id, quiz_name, quiz_owner, encoded_text):
        """
        Parses a quiz from its encoded text format.
        """
        questions = []
        categories = []

        # Split the text into lines to parse. We need an empty line at the end to finish the last section.
        lines = list(encoded_text.splitlines()) + [""]

        section = []
        next_section = []
        section_number = 0
        for line in lines:
            line = line.strip()
            section = next_section

            # Empty lines signify a new section
            if len(line) > 0:
                # Skip comment lines.
                if line[0] == "#":
                    continue

                # Append the current line to the current section.
                section.append(line)
                continue

            section_number += 1
            next_section = []

            # If the section is empty, skip it.
            if len(section) == 0:
                continue

            # First section contains the categories
            if section_number == 1:
                if len(section) == 1 and section[0] == ":None":
                    continue
                for name in section:
                    categories.append(Category(name, []))
                continue

            # Rest of the sections contain questions.
            text = section[0]
            encoded_question = section[1]
            question = Question.parse(text, encoded_question)
            questions.append(question)

            # The rest of the lines correspond to answer specs for categories.
            for index in range(len(section) - 2):
                encoded_answer_spec = section[2 + index]
                scoring_function = ScoringFunction.parse(encoded_answer_spec)
                answer_spec = AnswerSpec(question, scoring_function)
                categories[index].answer_specs.append(answer_spec)

        return Quiz(quiz_id, quiz_name, quiz_owner, questions, categories)

    @staticmethod
    def from_form(owner, form, errors):
        """ Parse a Quiz from the given form. """
        # Get the title of the quiz from the form.
        title = form.get("title", "")
        if len(title) == 0:
            errors.append("Please enter a quiz title")

        for key, value in form.items():
            print(key + " = " + value)

        # Get the categories of the quiz from the form.
        category_names = []
        category_answer_specs = {}
        category_number = 0
        while "category_{}_name".format(category_number + 1) in form:
            category_name = form.get("category_{}_name".format(category_number + 1), "")
            category_number += 1
            if category_number == "":
                errors.append("Please enter a category name for category {}".format(category_number))
                continue

            category_names.append(category_name)
            category_answer_specs[category_name] = []

        # Get the questions of the quiz out of the form.
        questions = []
        question_number = 0
        while "question_{}_text".format(question_number + 1) in form:
            # The prefix for all attributes about this question.
            prefix = "question_{}".format(question_number + 1)
            question_number += 1

            # Get the text of the question.
            question_text = form.get(prefix + "_text", "")
            if len(question_text) == 0:
                errors.append("Missing text for question {}".format(question_number))
                continue

            # Get the weighting of this question.
            question_weight_str = form.get(prefix + "_weight", "1")
            try:
                question_weight = float(question_weight_str)
            except ValueError:
                errors.append("Expected question weight to be a number, not: {}".format(question_weight_str))
                continue

            # Get the type of the question, and build the question accordingly.
            question_type = form.get(prefix + "_type")

            # Parse the question based on its type.
            question = None
            category_scoring_functions = None
            if question_type == "Multiple Choice":
                question, category_scoring_functions = MultiChoiceQuestion.from_form(
                    question_number, question_text, question_weight, form, category_names, errors
                )
            elif question_type == "Discrete Slider":
                question, category_scoring_functions = IntSliderQuestion.from_form(
                    question_number, question_text, question_weight, form, category_names, errors
                )
            elif question_type == "Continuous Slider":
                question, category_scoring_functions = FloatSliderQuestion.from_form(
                    question_number, question_text, question_weight, form, category_names, errors
                )
            else:
                errors.append("Unknown question type {} for question {}".format(question_type, question_number))
                continue

            # Register the question.
            if question is not None:
                if category_scoring_functions is None:
                    errors.append("Missing scoring functions for question {}".format(question_number))
                    continue

                # Add the question.
                questions.append(question)

                # Add its scoring functions for each category.
                for category_name, scoring_function in category_scoring_functions.items():
                    answer_spec = AnswerSpec(question, scoring_function)
                    category_answer_specs[category_name].append(answer_spec)

        # Create all of the categories.
        categories = []
        for category_name, answer_specs in category_answer_specs.items():
            category = Category(category_name, answer_specs)
            categories.append(category)

        # Create the quiz object.
        return Quiz(-1, title, owner, questions, categories)


class Category:
    """ A category that a user could be placed in based on their answers. """

    def __init__(self, name, answer_specs):
        self.name = name
        self.answer_specs = answer_specs

        # The db category associated with this question.
        self.db_category = None

    def get_db_category(self):
        """ Get the db category associated with this category, or None. """
        return self.db_category

    def set_db_category(self, db_category):
        """ Set the db category associated with this category. """
        self.db_category = db_category

    def get_answer_spec(self, question):
        """ Get the answer spec for the given question. """
        for answer_spec in self.answer_specs:
            if question == answer_spec.question:
                return answer_spec
        return None

    def __str__(self):
        """ Return the category as a string. """
        return "Category{name: " + self.name + "}"

    def __repr__(self):
        """ Return the category as a string. """
        return str(self)

    def __hash__(self):
        """ Hashes this category so it can be used in dictionaries. """
        return hash(id(self))

    @staticmethod
    def find_by_name(categories, category_name):
        """ Find a category with the given name in the given list, else returns None. """
        for category in categories:
            if category.name == category_name:
                return category
        return None


class UserAnswer:
    """ The answer a user made to a question in a quiz. """

    def __init__(self, uuid, user, question, answer):
        self.uuid = uuid
        self.user = user
        self.question = question
        self.answer = answer

        # The db answer associated with this answer.
        self.db_answer = None

    def get_db_answer(self):
        """ Get the db answer associated with this answer, or None. """
        return self.db_answer

    def set_db_answer(self, db_answer):
        """ Set the db answer associated with this answer. """
        self.db_answer = db_answer

    @staticmethod
    def read_answers_from_form(user, quiz, form):
        """ Reads a set of user answers from the given form. """
        # Get the ID for this set of answers.
        answers_uuid = form.get("answers_uuid", str(uuid.uuid4()))

        # Read the answers for each question.
        user_answers = []
        for index, question in enumerate(quiz.questions):
            answer = question.get_answer_from_form(form, index)
            user_answer = UserAnswer(answers_uuid, user, question, answer)
            user_answers.append(user_answer)
        return answers_uuid, user_answers


class AnswerSet:
    """ A set of answers a user has made to a quiz. """

    def __init__(self, quiz, answers_uuid, answers):
        self.quiz = quiz
        self.answers_uuid = answers_uuid
        self.answers = answers
        self.cached_scores = None

    def get_representative_id(self):
        """ Returns the lowest ID of any of the answers in this answer set. """
        min_id = None
        for answer in self.answers:
            if answer.get_db_answer() is None:
                continue

            answer_id = answer.get_db_answer().id
            if min_id is None or answer_id < min_id:
                min_id = answer_id
        return min_id

    def score_answers(self):
        """ Score the user's answers to this quiz. """
        # Check if we've already calculated the scores.
        if self.cached_scores is not None:
            return self.cached_scores

        # If we haven't, calculate them.
        category_scores = {}

        # Initialise the score for all categories to zero.
        for category in self.quiz.categories:
            category_scores[category] = 0

        # Score all of the answers.
        for user_answer in self.answers:
            # Skip answers the user has not entered.
            if user_answer.answer is None:
                continue

            # Score that answer for each category.
            for category in self.quiz.categories:
                answer_spec = category.get_answer_spec(user_answer.question)
                score = answer_spec.scoring_function.score(user_answer.answer)
                category_scores[category] += score

        # Cache the scores we found, and return them.
        self.cached_scores = category_scores
        return category_scores

    def find_best_matching_category(self):
        """ Returns the category that best matches this set of answers. """
        max_category = None
        max_category_score = None
        for category, score in self.score_answers().items():
            if max_category is None or score > max_category_score:
                max_category = category
                max_category_score = score
        return max_category

    @staticmethod
    def read_from_form(user, quiz, form):
        """ Reads a set of answers from the given form. """
        # Load the answers uuid and all of the answers.
        answers_uuid, answers = UserAnswer.read_answers_from_form(user, quiz, form)

        # Create and return the answer set.
        return AnswerSet(quiz, answers_uuid, answers)
