"""
This file contains functionality for parsing different
types of scoring functions for scoring user's answers.
"""

import math
from .encoding import parse_function, encode_function


class ScoringFunction:
    """ A function that can score an answer. """

    def __init__(self, fn_type):
        self.fn_type = fn_type

    def score(self, answer):
        """ Scores the given answer using this scoring function. """
        raise NotImplementedError

    def encode(self):
        """ Encodes this scoring function into a string to store in the database. """
        return encode_function(self.fn_type, self.encode_to_args())

    def encode_to_args(self):
        """ Encodes this scoring function into a list of arguments. """
        raise NotImplementedError

    @staticmethod
    def parse(encoded_fn):
        """ Parses the scoring function from the given text. """
        fn_type, args = parse_function(encoded_fn)

        if fn_type == "multi":
            return MultiScoringFunction.parse(args)
        if fn_type == "gaussian":
            return GaussianScoringFunction.parse(args)

        raise ValueError("Unknown scoring function " + fn_type)


class MultiScoringFunction(ScoringFunction):
    """ A function that gives a different score for each multi-choice option. """

    def __init__(self, option_scores):
        super(MultiScoringFunction, self).__init__("multi")
        self.option_scores = option_scores

    def score(self, answer):
        """ Scores the given answer using this scoring function. """
        int_answer = round(answer)
        if int_answer < 1 or int_answer > len(self.option_scores):
            return 0

        # Return the score corresponding to the given answer.
        return self.option_scores[int_answer - 1]

    def encode_to_args(self):
        """ Encodes this scoring function into a list of arguments. """
        return self.option_scores

    @staticmethod
    def parse(args):
        """ Parse a multi-choice scoring function from a set of arguments. """
        option_scores = []
        for arg in args:
            option_scores.append(float(arg))
        return MultiScoringFunction(option_scores)


def pdf(x, mu=0.0, sigma=1.0):
    x = float(x - mu) / sigma
    return math.exp(-x*x/2.0) / math.sqrt(2.0*math.pi) / sigma


class GaussianScoringFunction(ScoringFunction):
    """ A function that scores answers based on a gaussian curve. """

    def __init__(self, score_magnitude, peak_x, std_dev_x):
        super(GaussianScoringFunction, self).__init__("gaussian")
        self.score_magnitude = score_magnitude
        self.peak_x = peak_x
        self.std_dev_x = std_dev_x

    def score(self, answer):
        """
        Scores the given answer using an exponential decay curve
        centered on peak_x with a standard deviation of std_dev_x,
        and with a maximum value of score_magnitude.
        """
        # Normalise to a peak at 0, with a std. dev. of 1
        x = float(answer - self.peak_x) / self.std_dev_x
        # Calculate the exponential decay function, and scale it by the desired magnitude.
        return self.score_magnitude * math.exp(-x*x / 2.0)

    def encode_to_args(self):
        """ Encodes this scoring function into a list of arguments. """
        return [self.score_magnitude, self.peak_x, self.std_dev_x]

    @staticmethod
    def parse(args):
        """ Parse a gaussian scoring function from a set of arguments. """
        if len(args) != 3:
            raise ValueError("Expected three arguments: score_magnitude, peak_x, and std_dev_x")

        score_magnitude = float(args[0])
        peak_x = float(args[1])
        std_dev_x = float(args[2])
        return GaussianScoringFunction(score_magnitude, peak_x, std_dev_x)
