"""
Tests for question.py.
"""

from ..question import Question, MalformedQuestion, MultiChoiceQuestion, FloatSliderQuestion, IntSliderQuestion


def is_malformed(question, expected_text, expected_error=""):
    """
    Returns whether question is a MalformedQuestion with the text expected_text,
    and whether expected_error appears in the error of the question.
    """
    return isinstance(question, MalformedQuestion) \
           and question.text == expected_text and expected_error in question.error


def test_question_decoding():
    """ Tests for question string decoding. """
    q = "question"
    assert is_malformed(Question.parse(q, "apple"), q, "Missing opening bracket")
    assert is_malformed(Question.parse(q, "apple("), q, "Missing closing bracket")
    assert is_malformed(Question.parse(q, "apple()"), q, "Unknown question type")

    assert Question.parse(q, "multi()") == MultiChoiceQuestion(q, [])
    assert Question.parse(q, "multi(a,b,c)") == MultiChoiceQuestion(q, ["a", "b", "c"])
    assert Question.parse(q, "multi(\",\",3)") == MultiChoiceQuestion(q, [",", "3"])

    assert Question.parse(q, "float_slider(1, 2)") == FloatSliderQuestion(q, 1, 2)
    assert is_malformed(Question.parse(q, "float_slider(1,2,3)"), q, "Expected two arguments")
    assert is_malformed(Question.parse(q, "float_slider(a,2)"), q, "Expected min to be a number")
    assert is_malformed(Question.parse(q, "float_slider(1,b)"), q, "Expected max to be a number")

    assert Question.parse(q, "int_slider(1, 2)") == IntSliderQuestion(q, 1, 2, 1)
    assert is_malformed(Question.parse(q, "int_slider(1,2,3,4)"), q, "Expected two or three arguments")
    assert is_malformed(Question.parse(q, "int_slider(a,2)"), q, "Expected min to be an integer")
    assert is_malformed(Question.parse(q, "int_slider(1,b)"), q, "Expected max to be an integer")

    assert Question.parse(q, "int_slider(1, 2, 2)") == IntSliderQuestion(q, 1, 2, 2)
    assert is_malformed(Question.parse(q, "int_slider(a,2, 2)"), q, "Expected min to be an integer")
    assert is_malformed(Question.parse(q, "int_slider(1,b, 2)"), q, "Expected max to be an integer")
    assert is_malformed(Question.parse(q, "int_slider(1,2,c)"), q, "Expected step to be an integer")


def test_question_encoding():
    """ Tests for question string encoding """
    q = "question"
    assert "multi()" == MultiChoiceQuestion(q, []).encode()
    assert "multi(a,b,c)" == MultiChoiceQuestion(q, ["a", "b", "c"]).encode()
    assert "multi(\",\",3)" == MultiChoiceQuestion(q, [",", "3"]).encode()

    assert "float_slider(1.0,2.0)" == FloatSliderQuestion(q, 1, 2).encode()
    assert "float_slider(0.0,10.0)" == FloatSliderQuestion(q, 0, 10).encode()

    assert "int_slider(1,2,4)" == IntSliderQuestion(q, 1, 2, 4).encode()
    assert "int_slider(0,10,5)" == IntSliderQuestion(q, 0, 10, 5).encode()
