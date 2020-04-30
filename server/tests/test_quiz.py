#
# Some question tests.
#

from ..quiz import parse_question, MalformedQuestion, MultiChoiceQuestion, SliderQuestion



def is_malformed(question, expected_text, expected_error=""):
    """
    Returns whether question is a MalformedQuestion with the text expected_text,
    and whether expected_error appears in the error of the question.
    """
    return isinstance(question, MalformedQuestion) and question.text == expected_text and expected_error in question.error

def test_question_decoding():
    """ Tests for question string decoding. """

    q = "question"
    assert is_malformed(parse_question(q, "apple"), q, "Missing opening bracket")
    assert is_malformed(parse_question(q, "apple("), q, "Missing closing bracket")
    assert is_malformed(parse_question(q, "apple()"), q, "Unknown question type")

    assert parse_question(q, "multi()") == MultiChoiceQuestion(q, [])
    assert parse_question(q, "multi(a,b,c)") == MultiChoiceQuestion(q, ["a", "b", "c"])
    assert parse_question(q, "multi(\",\",3)") == MultiChoiceQuestion(q, [",", "3"])

    assert parse_question(q, "slider(1, 2)") == SliderQuestion(q, 1, 2)
    assert is_malformed(parse_question(q, "slider(1,2,3)"), q, "Expected two arguments")
    assert is_malformed(parse_question(q, "slider(a,2)"), q, "Expected min to be a number")
    assert is_malformed(parse_question(q, "slider(1,b)"), q, "Expected max to be a number")

def test_question_encoding():
    """ Tests for question string encoding """

    q = "question"
    assert "multi()" == MultiChoiceQuestion(q, []).encode()
    assert "multi(a,b,c)" == MultiChoiceQuestion(q, ["a", "b", "c"]).encode()
    assert "multi(\",\",3)" == MultiChoiceQuestion(q, [",", "3"]).encode()

    assert "slider(1,2)" == SliderQuestion(q, 1, 2).encode()
    assert "slider(0,10)" == SliderQuestion(q, 0, 10).encode()
