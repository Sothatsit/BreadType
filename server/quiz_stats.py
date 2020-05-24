"""
Manages the collation of statistics about user's responses to quizzes.
"""

import random
from .user_model import load_answers_of_question
from .quiz import AnswerSet


class QuizStatistics:
    """
    Stores and gives access to the statistics of a quiz.
    """

    # The colours to use in the statistic graphs.
    GRAPH_COLOURS = ["rgb(255, 99, 132)", "rgb(54, 162, 235)", "rgb(255, 205, 86)", "#98fb98"] * 5

    def __init__(self, quiz, question_stats):
        self.quiz = quiz
        self.question_stats = question_stats

    def build_answer_sets(self):
        """ Groups the answers to all of the questions into their respective answer sets. """
        # Group all of the answers by their answer set uuid.
        answers_by_uuid = {}
        for stats in self.question_stats:
            for answer in stats.answers:
                if answer.uuid in answers_by_uuid:
                    answers_by_uuid[answer.uuid].append(answer)
                else:
                    answers_by_uuid[answer.uuid] = [answer]

        # Create and return the answer set objects.
        answer_sets = []
        for uuid, answers in answers_by_uuid.items():
            answer_set = AnswerSet(self.quiz, uuid, answers)
            answer_sets.append(answer_set)
        return answer_sets

    def get_category_breakdown_counts(self):
        """ Returns a map from category name to the number of users who got placed into that category. """
        # Get the answers that all the users gave.
        answer_sets = self.build_answer_sets()

        # Initialise a dictionary to store the amount of times each user got placed in each category.
        category_counts = {}
        for category in self.quiz.categories:
            category_counts[category.name] = 0

        # Populate the dictionary of category counts.
        for answer_set in answer_sets:
            category = answer_set.find_best_matching_category()
            # Only needed because of old quizzes.
            if category is None:
                continue
            category_counts[category.name] += 1
        return category_counts

    def get_category_breakdown(self):
        """ Returns a map from category name to the percentage of users who got placed into that category. """
        # Get the number of responses for each category.
        category_counts = self.get_category_breakdown_counts()

        # Determine the total count between all categories.
        total_count = 0
        for count in category_counts.values():
            total_count += count

        # Calculate the percentage of responses that were each category.
        category_percents = {}
        for category_name, count in category_counts.items():
            category_percents[category_name] = 100.0 * count / total_count
        return category_percents

    def get_highest_placed_category(self):
        """ Returns the name of the highest placed category, and the percentage of people who got it. """
        max_category_name = None
        max_percentage = None
        for category_name, percentage in self.get_category_breakdown().items():
            if max_category_name is None or percentage > max_percentage:
                max_category_name = category_name
                max_percentage = percentage
        return max_category_name, max_percentage

    def generate_category_breakdown_html(self):
        """ Creates the HTML for displaying a pie chart of the category breakdown. """
        # Calculate the data to be shown in the graph.
        category_breakdown = self.get_category_breakdown_counts()
        keys = []
        values = []
        colors = []
        value_sum = 0
        for index, (key, value) in enumerate(category_breakdown.items()):
            keys.append('"' + key + '"')
            values.append(str(value))
            colors.append('"' + QuizStatistics.GRAPH_COLOURS[index] + '"')
            value_sum += value

        # If there is no data, there is no point displaying a graph.
        if value_sum == 0:
            return "No data"

        # Generate the HTML to display the graph.
        html = "<canvas id=\"category_breakdown_chart\"></canvas>\n"
        html += "<script>\n"
        html += "var category_breakdown_ctx = $('#category_breakdown_chart');\n"
        html += "var category_breakdown_data = {\n"
        html += "  datasets: [{ data: [" + ", ".join(values) + "],\n"
        html += "               backgroundColor: [" + ", ".join(colors) + "] }],\n"
        html += "  labels: [" + ", ".join(keys) + "]\n"
        html += "};\n"
        html += "var category_breakdown_chart = new Chart(category_breakdown_ctx, {\n"
        html += "  type: 'pie', data: category_breakdown_data\n"
        html += "});\n"
        html += "</script>\n"
        return html

    @staticmethod
    def collect_statistics(quiz):
        """ Collect the statistics for the given quiz. """
        question_stats = []
        for question in quiz.questions:
            question_stats.append(QuestionStatistics.collect_statistics(question))
        return QuizStatistics(quiz, question_stats)


class QuestionStatistics:
    """
    Stores and gives access to the statistics of a question in a quiz.
    """

    def __init__(self, question, answers):
        self.question = question
        self.answers = answers

    def get_multi_breakdown(self):
        """ Returns a map from the name of each multi-choice option to the number of responses. """
        # Initialise to zero for all multi-choice options.
        response_counts = {}
        for option in self.question.options:
            response_counts[option] = 0

        # Count the number of responses for each option.
        for answer in self.answers:
            answer_index = int(answer.answer) - 1
            if answer_index < 0 or answer_index >= len(self.question.options):
                continue
            response_counts[self.question.options[answer_index]] += 1
        return response_counts

    def get_slider_breakdown(self):
        """ Returns a list of tuples of the name of each bucket and the number of responses in that bucket. """
        # Determine the number of buckets to generate.
        min_val = self.question.min_value
        max_val = self.question.max_value
        if self.question.question_type == "int_slider":
            bucket_count = (max_val - min_val) // self.question.step + 1
        else:
            bucket_count = 10

        # Determine characteristics of the buckets.
        bucket_width = (max_val - min_val) / bucket_count

        # Generate the buckets.
        bucket_names = []
        bucket_counts = []
        for bucket_index in range(bucket_count):
            if self.question.question_type == "int_slider":
                bucket_name = str(min_val + bucket_index * self.question.step)
            else:
                bucket_from = min_val + bucket_index * bucket_width
                bucket_to = min_val + (bucket_index + 1) * bucket_width
                bucket_name = "{:.1f}".format((bucket_from + bucket_to) / 2)
            bucket_names.append(bucket_name)
            bucket_counts.append(0)

        # Populate the buckets.
        for answer in self.answers:
            # Determine which bucket the answer falls into.
            if self.question.question_type == "int_slider":
                bucket_index = (answer.answer - min_val) // self.question.step
            else:
                bucket_index = round((answer.answer - min_val) / (max_val - min_val) * bucket_count)

            # Add this statistic to its bucket.
            bucket_index = int(bucket_index)
            if bucket_index < 0 or bucket_index >= bucket_count:
                continue
            bucket_counts[bucket_index] += 1

        # Return the buckets and their names.
        return list(zip(bucket_names, bucket_counts))

    def generate_answer_summary_html(self):
        """ Generates the HTML for displaying a graph of the answers. """
        quid = str(self.question.get_db_question().id)
        html = "<canvas id=\"question_" + quid + "_chart\" class=\"question_chart\"></canvas>\n"

        # Generate the data for the different question types.
        if self.question.question_type == "multi":
            # Generate the data to populate the graph with.
            keys = []
            values = []
            colors = []
            value_sum = 0
            for index, (key, value) in enumerate(self.get_multi_breakdown().items()):
                keys.append('"' + key + '"')
                values.append(str(value))
                colors.append('"' + QuizStatistics.GRAPH_COLOURS[index] + '"')
                value_sum += value
        elif self.question.question_type == "int_slider" or self.question.question_type == "float_slider":
            # Generate the data to populate the graph with.
            keys = []
            values = []
            colors = []
            colour = QuizStatistics.GRAPH_COLOURS[random.randrange(0, len(QuizStatistics.GRAPH_COLOURS) - 1)]
            value_sum = 0
            for index, (key, value) in enumerate(self.get_slider_breakdown()):
                keys.append('"' + key + '"')
                values.append(str(value))
                colors.append('"' + colour + '"')
                value_sum += value
        else:
            return "Unknown question type"

        # If there is no data, don't graph nothing.
        if value_sum == 0:
            return "No data"

        # Create the HTML that will populate the graph.
        html += "<script>\n"
        html += "var question_" + quid + "_ctx = $('#question_" + quid + "_chart');\n"
        html += "var question_" + quid + "_data = {\n"
        html += "  datasets: [{ data: [" + ", ".join(values) + "],\n"
        html += "               backgroundColor: [" + ", ".join(colors) + "] }],\n"
        html += "  labels: [" + ", ".join(keys) + "]\n"
        html += "};\n"
        html += "var question_" + quid + "_chart = new Chart(question_" + quid + "_ctx, {\n"
        html += "  type: 'bar', data: question_" + quid + "_data,\n"
        html += "  options: {legend: {display: false},\n"
        html += "            scales: {yAxes: [{ticks: {beginAtZero: true,\n"
        html += "            callback: function(value) {if (value % 1 === 0) {return value;}}}}]}}"
        html += "});\n"
        html += "</script>\n"
        return html

    @staticmethod
    def collect_statistics(question):
        """ Collect the statistics for the given question. """
        answers = load_answers_of_question(question)
        return QuestionStatistics(question, answers)
