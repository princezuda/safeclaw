"""Core summarization logic using sumy (extractive, no LLM)."""

from __future__ import annotations

import re

import httpx
from bs4 import BeautifulSoup
from sumy.nlp.stemmers import Stemmer
from sumy.nlp.tokenizers import Tokenizer
from sumy.parsers.plaintext import PlaintextParser
from sumy.summarizers.lsa import LsaSummarizer
from sumy.utils import get_stop_words

LANGUAGE = "english"
_HEADERS = {
    "User-Agent": "tldr-feed/0.1 (extractive summarizer; +https://github.com/tldr-feed/tldr-feed)"
}


def fetch_text(url: str, *, timeout: float = 15.0) -> str:
    """Fetch a URL and return the main body text."""
    resp = httpx.get(url, headers=_HEADERS, timeout=timeout, follow_redirects=True)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "lxml")

    # Remove noise
    for tag in soup(["script", "style", "nav", "header", "footer", "aside", "form"]):
        tag.decompose()

    # Prefer <article> or <main>, fall back to <body>
    container = soup.find("article") or soup.find("main") or soup.find("body")
    if container is None:
        return ""

    text = container.get_text(separator="\n", strip=True)
    # Collapse blank lines
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text


def summarize(text: str, sentences: int = 3) -> str:
    """Return an extractive summary of *text* using LSA."""
    if not text.strip():
        return ""

    parser = PlaintextParser.from_string(text, Tokenizer(LANGUAGE))
    stemmer = Stemmer(LANGUAGE)
    summarizer = LsaSummarizer(stemmer)
    summarizer.stop_words = get_stop_words(LANGUAGE)

    result = summarizer(parser.document, sentences)
    return " ".join(str(s) for s in result)


def tldr(url: str, sentences: int = 3) -> str:
    """Fetch a URL and return a short extractive summary."""
    text = fetch_text(url)
    if not text:
        return "(no readable text found)"
    return summarize(text, sentences=sentences)
