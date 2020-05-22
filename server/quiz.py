"""
Holds the server classes for representing quizzes and their categories.
"""

from .question import Question, AnswerSpec


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

    def score_responses(self, form):
        """ Score the user's responses to this quiz. """
        category_scores = {}

        # Initialise the score for all categories to zero.
        for category in self.categories:
            category_scores[category] = 0

        # Score all of the answers
        for index, question in enumerate(self.questions):
            answer = question.get_answer_from_form(form, index)
            # Skip answers the user has not entered.
            if answer is None:
                continue

            for category in self.categories:
                answer_spec = category.get_answer_spec(question)
                category_scores[category] += question.score_answer(answer, answer_spec)

        return category_scores

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
                encoded += answer_spec.encoded + "\n"
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
                answer_spec = AnswerSpec(question, encoded_answer_spec)
                categories[index].answer_specs.append(answer_spec)

        return Quiz(quiz_id, quiz_name, quiz_owner, questions, categories)


class Category:
    """ A category that a user could be placed in based on their answers. """

    def __init__(self, name, answer_specs):
        self.name = name
        self.answer_specs = answer_specs

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