"""
This file contains utility functions for the encoding and decoding of questions and sorting functions.
"""

import csv
from io import StringIO


def parse_function(encoded):
    """
    Parses the given encoded function string into its name and arguments.
    e.g. "multi(a, b, c)" -> ("multi", ["a", "b", "c"])
    :return: (function_name, [arg1, arg2, ..., argN])
    """
    # Special shortened format for multi choice scoring.
    if len(encoded) > 0 and encoded[0] == "[" and encoded[-1] == "]":
        encoded = "multi(" + encoded[1:-1] + ")"

    opening_bracket_index = encoded.find("(")
    if opening_bracket_index < 0:
        raise ValueError("Missing opening bracket in \"" + encoded + "\"")

    closing_bracket_index = encoded.find(")")
    if closing_bracket_index < 0:
        raise ValueError("Missing closing bracket in \"" + encoded + "\"")
    if closing_bracket_index != len(encoded) - 1:
        raise ValueError("Text after closing bracket of function: \"" + encoded[closing_bracket_index + 1:] + "\"")

    # Extract the function name and the arguments as strings from the encoded str.
    function_name = encoded[:opening_bracket_index]
    args_str = encoded[opening_bracket_index + 1:closing_bracket_index]

    # Decode the arguments list in the CSV format.
    args = list(csv.reader([args_str]))[0]

    # Return the function name and arguments as a tuple.
    return function_name, args


def encode_function(function_name, args):
    """
    Encode a function name and arguments as a string.
    e.g. ("multi", ["a", "b", "c"]) -> "multi(a, b, c)"
    :return: the function encoded as a string.
    """
    # Encode the arguments into a CSV string.
    args_str_io = StringIO()
    csv.writer(args_str_io).writerow(args)
    args_str = args_str_io.getvalue().strip()
    args_str_io.close()

    # Combine the type of this question and the CSV encoded arguments into one string.
    return function_name + "(" + args_str + ")"
