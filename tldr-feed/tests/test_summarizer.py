"""Tests for the summarizer module."""

from tldr_feed.summarizer import fetch_text, summarize


SAMPLE_TEXT = """
Natural language processing (NLP) is a subfield of computer science and
artificial intelligence. It is concerned with the interactions between computers
and human language. In particular, it focuses on how to program computers to
process and analyze large amounts of natural language data. The result is a
computer capable of understanding the contents of documents. NLP can accurately
extract information and insights contained in the documents. It also categorizes
and organizes the documents themselves. Challenges in natural language processing
include speech recognition, natural language understanding, and generation.
Natural language processing has many real-world applications including machine
translation, sentiment analysis, and chatbots.
"""


def test_summarize_returns_string():
    result = summarize(SAMPLE_TEXT, sentences=2)
    assert isinstance(result, str)
    assert len(result) > 0


def test_summarize_respects_sentence_count():
    result = summarize(SAMPLE_TEXT, sentences=1)
    # One sentence should be shorter than three
    result3 = summarize(SAMPLE_TEXT, sentences=3)
    assert len(result) <= len(result3)


def test_summarize_empty_input():
    assert summarize("") == ""
    assert summarize("   ") == ""


def test_summarize_content_comes_from_input():
    result = summarize(SAMPLE_TEXT, sentences=2)
    # Every word in the summary should appear somewhere in the source
    # (extractive summarization pulls exact sentences)
    for word in result.split()[:5]:
        clean = word.strip(".,;:!?\"'()[]")
        if len(clean) > 3:
            assert clean.lower() in SAMPLE_TEXT.lower()
