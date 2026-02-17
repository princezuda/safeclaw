# tldr-feed

**Paste a URL, get a summary. No AI, just math.**

`tldr-feed` is a command-line tool that fetches any web page and returns a short extractive summary using [LSA (Latent Semantic Analysis)](https://en.wikipedia.org/wiki/Latent_semantic_analysis). No LLM, no API keys, no cloud — runs 100% locally.

---

## Install

```bash
pip install tldr-feed
```

## Usage

```bash
# Summarize any URL (default: 3 sentences)
tldr-feed https://example.com/some-article

# Get a longer summary
tldr-feed https://example.com/some-article -n 5

# Plain text output (no formatting, good for piping)
tldr-feed https://example.com/some-article --raw
```

### Example

```
$ tldr-feed https://en.wikipedia.org/wiki/Latent_semantic_analysis

╭─────────────────────── TL;DR ───────────────────────╮
│ Latent semantic analysis is a technique in natural   │
│ language processing of analyzing relationships       │
│ between a set of documents and the terms they        │
│ contain by producing a set of concepts related to    │
│ the documents and terms.                             │
╰─────────────────────────────────────────────────────╯
```

## How it works

1. Fetches the page with `httpx`
2. Strips navigation, ads, and boilerplate with `BeautifulSoup`
3. Extracts the key sentences using LSA via `sumy`

That's it. No tokens. No prompts. No API bills.

## As a library

```python
from tldr_feed.summarizer import tldr

summary = tldr("https://example.com/article", sentences=3)
print(summary)
```

## Why?

- **Free** — no API keys, no usage limits
- **Fast** — summarizes most pages in under 2 seconds
- **Private** — nothing leaves your machine
- **Deterministic** — same input, same output, every time
- **Tiny** — under 200 lines of code

## License

MIT
