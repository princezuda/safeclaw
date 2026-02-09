# SafeClaw 🐾

**The zero-cost alternative to OpenClaw. No LLM. No API bills. No prompt injection. Runs on any machine.**

While OpenClaw users are burning [$200/day](https://www.notebookcheck.net/Free-to-use-AI-tool-can-burn-through-hundreds-of-Dollars-per-day-OpenClaw-has-absurdly-high-token-use.1219925.0.html) and [$3,600/month](https://dev.to/thegdsks/i-tried-the-free-ai-agent-with-124k-github-stars-heres-my-500-reality-check-2885) on API tokens, SafeClaw delivers 90% of the functionality using traditional programming — rule-based parsing, ML pipelines, and local-first tools. **Your API bill: $0. Forever.**

SafeClaw uses VADER, spaCy, sumy, YOLO, Whisper, Piper, and other battle-tested ML techniques instead of generative AI. The result: deterministic, predictable, private, and completely free to run.

---

## Why SafeClaw?

| | SafeClaw | OpenClaw |
|---|---|---|
| **Monthly cost** | **$0** | $100–$3,600+ |
| **Requires LLM** | No | Yes |
| **Prompt injection risk** | **None** | Yes |
| **Works offline** | **Yes** (core features) | No |
| **Runs on any machine** | **Yes** (Linux, macOS, Windows) | Needs powerful hardware or cloud APIs |
| **Deterministic output** | **Yes** | No (LLM responses vary) |
| **Privacy** | **Local by default** (external only when you ask, e.g. weather) | Data sent to API providers |

---

## Features

### 🗣️ Voice Control
* **Speech-to-Text** — Whisper STT runs locally, no cloud transcription
* **Text-to-Speech** — Piper TTS for natural voice output, completely offline
* **Voice-first workflow** — Talk to SafeClaw like you would any assistant

### 🏠 Smart Home & Device Control
* **Smart home integration** — Control your connected devices
* **Bluetooth device control** — Discover and manage Bluetooth devices
* **Network scanning** — Device discovery on your local network

### 📱 Social Media Intelligence
* **Twitter/X summarization** — Add accounts, get summaries of their activity
* **Mastodon summarization** — Follow and summarize fediverse accounts
* **Bluesky summarization** — Track and summarize Bluesky feeds
* No API tokens needed for public content

### 📰 RSS News Aggregation
* **50+ preset feeds** — Hacker News, Ars Technica, BBC, Reuters, Nature, and more
* **8 categories** — Tech, World, Science, Business, Programming, Security, Linux, AI
* **Custom feeds** — Import any RSS/Atom feed
* **Auto-summarization** — Extractive summaries with sumy (no AI)
* **Per-user preferences** — Customize your news sources

### 🔒 Privacy First
* **Self-hosted by default** — Your data stays local unless you explicitly request external info (like weather)
* **No API keys required** — Core features work completely offline
* **No cloud AI dependencies** — No tokens sent to OpenAI, Anthropic, or Google
* **No prompt injection** — No LLM means no injection attacks

### 📡 Multi-Channel
* **CLI** — Interactive command line with Rich formatting
* **Telegram** — Full bot integration
* **Discord** — Coming soon
* **Slack** — Coming soon
* **Webhooks** — Inbound and outbound support

### ⚡ Automation
* **Command chaining** — Combine actions naturally: "read my email and remind me at 3pm"
* **Web crawling** — Async crawling with depth limits and domain filtering
* **Summarization** — LexRank, TextRank, LSA, Luhn algorithms
* **Reminders** — Natural language time parsing with dateparser
* **Shell commands** — Sandboxed command execution
* **File operations** — Search, list, read files
* **Cron jobs** — Scheduled task automation
* **Daily briefings** — Weather, reminders, news from your feeds

### 📊 Text Analysis
* **VADER Sentiment** — Lexicon-based sentiment analysis
* **Keyword Extraction** — TF-IDF style extraction
* **Readability Scoring** — Flesch-Kincaid metrics

### 📧 Email Integration
* **IMAP Support** — Read emails from Gmail, Outlook, Yahoo
* **SMTP Support** — Send emails
* **Standard protocols** — No API keys required

### 📅 Calendar Support
* **ICS Files** — Import and parse .ics calendar files
* **CalDAV** — Connect to Google Calendar, iCloud (optional)
* **Event filtering** — Today, upcoming, by date range

### 📄 Document Reading
* **PDF** — Text extraction with PyMuPDF
* **DOCX** — Microsoft Word documents
* **HTML/Markdown/TXT** — Plain text formats

### 🔔 Notifications
* **Desktop notifications** — Cross-platform (macOS, Windows, Linux)
* **Priority levels** — Low, normal, high, urgent
* **Rate limiting** — Prevent notification spam

### 👁️ Optional ML Features
* **NLP** — spaCy named entity recognition (~50MB)
* **Vision** — YOLO object detection + OCR (~2GB)
* **OCR** — Tesseract text extraction from images (lightweight)

### 🥚 Easter Eggs
* Built-in personality and hidden surprises — because tools should be fun

---

## Full Comparison: SafeClaw vs OpenClaw

| Feature | SafeClaw | OpenClaw |
|---|---|---|
| Self-hosted | ✅ | ✅ |
| Cross-platform (Linux, macOS, Windows) | ✅ | ✅ |
| No AI/LLM required | ✅ | ❌ |
| Offline capable | ✅ | ❌ |
| Zero API cost | ✅ | ❌ |
| No prompt injection | ✅ | ❌ |
| Privacy-first | ✅ (local by default) | ✅ |
| Voice (STT/TTS) | ✅ (Whisper + Piper, local) | ✅ (ElevenLabs, paid API) |
| Smart home control | ✅ | ✅ (via skills) |
| Bluetooth control | ✅ | ❌ |
| Network scanning | ✅ | ❌ |
| Social media summaries | ✅ (Twitter, Mastodon, Bluesky) | ❌ (requires separate skills) |
| Multi-channel | ✅ (CLI, Telegram, Webhooks) | ✅ (13+ platforms) |
| Web crawling | ✅ | ✅ |
| Summarization | ✅ (extractive) | ✅ (AI-generated) |
| RSS/News feeds | ✅ (50+ feeds) | ✅ (via skills) |
| Sentiment analysis | ✅ (VADER) | ✅ (AI) |
| Email integration | ✅ | ✅ |
| Calendar support | ✅ | ✅ |
| Document reading | ✅ | ✅ |
| Desktop notifications | ✅ | ✅ |
| Object detection | ✅ (YOLO) | ❌ |
| OCR | ✅ (Tesseract) | ❌ |
| Cron jobs | ✅ | ✅ |
| Webhooks | ✅ | ✅ |
| Plugin system | ✅ | ✅ (5,700+ skills) |
| Free-form chat | ❌ | ✅ |
| Creative writing | ❌ | ✅ |
| Command chaining | ✅ ("read email and remind me at 3pm") | ✅ |
| Autonomous multi-step tasks | ❌ | ✅ |
| Self-writing skills | ❌ | ✅ |
| Browser automation | ❌ | ✅ |

---

## Installation

### Using pipx (recommended)

```bash
# Install pipx if needed
# Linux:
sudo apt install pipx
# macOS:
brew install pipx

pipx ensurepath

# Install SafeClaw
pipx install safeclaw
```

### Using pip with virtual environment

```bash
# Create and activate venv
python3 -m venv ~/.safeclaw-venv
source ~/.safeclaw-venv/bin/activate

# Install SafeClaw
pip install safeclaw
```

### From source

```bash
git clone https://github.com/princezuda/safeclaw.git
cd safeclaw
pip install -e .
```

### Optional ML Features

```bash
# NLP - spaCy named entity recognition (~50MB)
pip install safeclaw[nlp]

# Vision - YOLO object detection + OCR (~2GB, requires PyTorch)
pip install safeclaw[vision]

# OCR only - text extraction from images (lightweight, requires Tesseract)
pip install safeclaw[ocr]

# All ML features
pip install safeclaw[ml]
```

**Requirements:** Python 3.11+, ~50MB disk (base), ~2GB additional for vision features. Runs on Linux, macOS, and Windows.

---

## Quick Start

```bash
# Start interactive mode
safeclaw

# Or with verbose logging
safeclaw --verbose
```

### Example Commands

```
> news                              # Get headlines from enabled feeds
> news tech                         # Get tech news only
> news categories                   # See all available categories
> news enable science               # Enable science feeds
> add feed https://blog.example.com/rss  # Add custom feed
> summarize https://news.ycombinator.com
> crawl https://example.com
> remind me to call mom tomorrow at 3pm
> morning briefing                  # Includes news from your feeds!
> check my email                    # View inbox (requires setup)
> read my email and remind me at 3pm # Chain commands naturally
> calendar today                    # Today's events from .ics
> analyze sentiment of this text    # VADER sentiment analysis
> read document.pdf                 # Extract text from documents
> help
```

### CLI Commands

```bash
# News
safeclaw news                       # Headlines from enabled categories
safeclaw news tech                  # Tech news only
safeclaw news --categories          # List all categories
safeclaw news world -n 20           # 20 world news headlines
safeclaw news --add https://blog.example.com/rss --name "My Blog"
safeclaw news -s                    # With auto-summarization

# Summarize
safeclaw summarize https://example.com/article -n 5

# Crawl
safeclaw crawl https://example.com --depth 2

# Text analysis
safeclaw analyze "This product is amazing! I love it."
safeclaw analyze document.txt --no-readability

# Documents
safeclaw document report.pdf
safeclaw document paper.docx --summarize -n 5
safeclaw document notes.md --output extracted.txt

# Calendar
safeclaw calendar import --file calendar.ics
safeclaw calendar today
safeclaw calendar upcoming --days 14

# Webhooks
safeclaw webhook --port 8765

# Initialize config
safeclaw init
```

---

## Configuration

SafeClaw looks for configuration in `config/config.yaml`:

```yaml
safeclaw:
  name: "SafeClaw"
  language: "en"
  timezone: "UTC"

channels:
  cli:
    enabled: true
  webhook:
    enabled: true
    port: 8765
  telegram:
    enabled: false
    token: "YOUR_BOT_TOKEN"

actions:
  shell:
    enabled: true
    sandboxed: true
    timeout: 30
  files:
    enabled: true
    allowed_paths:
      - "~"
```

---

## Architecture

```
┌──────────────────────────────────────────────────────────────────────┐
│                           SAFECLAW                                   │
├──────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌────────────┐  │
│  │  CHANNELS   │  │   ACTIONS   │  │  TRIGGERS   │  │    CORE    │  │
│  ├─────────────┤  ├─────────────┤  ├─────────────┤  ├────────────┤  │
│  │ • CLI       │  │ • Files     │  │ • Cron      │  │ • Analyzer │  │
│  │ • Telegram  │  │ • Shell     │  │ • Webhooks  │  │ • Documents│  │
│  │ • Webhooks  │  │ • Crawl     │  │ • Watchers  │  │ • Notify   │  │
│  │ • Discord   │  │ • Summarize │  │ • Events    │  │ • Feeds    │  │
│  └─────────────┘  │ • Reminder  │  └─────────────┘  │ • Crawler  │  │
│                   │ • Briefing  │                   │ • Summary  │  │
│  ┌─────────────┐  │ • News/RSS  │  ┌─────────────┐  │ • Voice    │  │
│  │   VOICE     │  │ • Email     │  │  DEVICES    │  │ • Social   │  │
│  ├─────────────┤  │ • Calendar  │  ├─────────────┤  └────────────┘  │
│  │ • Whisper   │  │ • Social    │  │ • Bluetooth │                  │
│  │ • Piper TTS │  └─────────────┘  │ • Network   │                  │
│  └─────────────┘                   │ • Smart Home│                  │
│                                    └─────────────┘                  │
│                                                                      │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │                  COMMAND PARSER                                │  │
│  │   Keyword + Regex + Fuzzy Match + Date Parser + NLP           │  │
│  └───────────────────────────────────────────────────────────────┘  │
│                                                                      │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │                  MEMORY (SQLite)                               │  │
│  │   History • Preferences • Reminders • Cache • Events          │  │
│  └───────────────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────────────┘
```

---

## How It Works (No AI!)

### Command Parsing

Instead of burning tokens on LLMs, SafeClaw uses:

1. **Keyword matching** — Fast lookup of command keywords
2. **Regex patterns** — Structured extraction of parameters
3. **Fuzzy matching** — Typo tolerance with rapidfuzz
4. **Date parsing** — Natural language dates with dateparser

```
# Example: "remind me to call mom tomorrow at 3pm"
# → intent: "reminder"
# → params: {task: "call mom", time: "tomorrow at 3pm"}
# → entities: {datetime: 2024-01-16 15:00:00}
```

### Voice Pipeline

Fully local voice processing — no cloud APIs, no per-minute billing:

* **Whisper STT** — OpenAI's Whisper model running locally for speech recognition
* **Piper TTS** — Fast, high-quality text-to-speech with multiple voice options

### Summarization

Uses [sumy](https://github.com/miso-belica/sumy)'s extractive algorithms:

* **LexRank** — Graph-based, like PageRank for sentences
* **TextRank** — Word co-occurrence graphs
* **LSA** — Latent Semantic Analysis
* **Luhn** — Statistical word frequency

No neural networks, no API calls — pure math.

### Social Media Summarization

Add Twitter, Mastodon, or Bluesky accounts and get extractive summaries of their recent posts. No API tokens needed for public content. Useful for tracking industry voices, news accounts, or competitors without doomscrolling.

### Web Crawling

Async crawling with httpx + BeautifulSoup:

* Single page link extraction
* Multi-page crawling with depth limits
* Domain filtering and pattern matching
* Built-in caching

---

## Extending SafeClaw

### Custom Actions

```python
from safeclaw.actions.base import BaseAction

class MyAction(BaseAction):
    name = "myaction"

    async def execute(self, params, user_id, channel, engine):
        # Your logic here
        return "Action completed!"

# Register it
engine.register_action("myaction", MyAction().execute)
```

### Custom Intent Patterns

Add to `config/intents.yaml`:

```yaml
intents:
  deploy:
    keywords: ["deploy", "release", "ship"]
    patterns:
      - "deploy to (production|staging)"
    examples:
      - "deploy to production"
    action: "webhook"
```

### Plugin System

Plugins are automatically loaded from the plugins directory:

```
src/safeclaw/plugins/
├── official/          # Curated, tested plugins
│   └── smarthome.py
├── community/         # User-contributed plugins
│   └── your_plugin.py
├── base.py            # BasePlugin class
└── loader.py          # Plugin loader
```

---

## Who Is SafeClaw For?

**SafeClaw is for you if:**
* You want automation without API bills
* You're tired of unpredictable OpenClaw costs
* Privacy matters to you — your data stays local by default
* You prefer deterministic, predictable behavior
* You want voice control without paying for ElevenLabs
* You need social media monitoring without the doomscroll
* You want smart home and Bluetooth control in one tool
* You don't need free-form AI conversation

**Stick with OpenClaw if:**
* You need autonomous multi-step reasoning
* Free-form conversation is essential
* You want the AI to write its own skills
* Browser automation is a core need

---

## Development

```bash
# Clone the repo
git clone https://github.com/princezuda/safeclaw.git
cd safeclaw

# Install dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Type checking
mypy src/safeclaw

# Linting
ruff check src/safeclaw
```

---

## License

MIT License — see [LICENSE](LICENSE) for details.

## Contributing

Contributions welcome! Areas we'd love help with:

* More channel adapters (Discord, Slack, Matrix)
* Smart home integrations (Home Assistant, Philips Hue)
* Better intent patterns
* Additional social media platforms
* Documentation improvements
* Tests and CI/CD

## Acknowledgments

* [Whisper](https://github.com/openai/whisper) — Local speech-to-text
* [Piper](https://github.com/rhasspy/piper) — Local text-to-speech
* [sumy](https://github.com/miso-belica/sumy) — Extractive summarization
* [VADER](https://github.com/cjhutto/vaderSentiment) — Sentiment analysis
* [feedparser](https://github.com/kurtmckee/feedparser) — RSS/Atom feed parsing
* [dateparser](https://github.com/scrapinghub/dateparser) — Natural language date parsing
* [rapidfuzz](https://github.com/maxbachmann/RapidFuzz) — Fast fuzzy matching
* [httpx](https://github.com/encode/httpx) — Async HTTP client
* [FastAPI](https://fastapi.tiangolo.com/) — Webhook server
* [Rich](https://github.com/Textualize/rich) — Beautiful CLI output
* [PyMuPDF](https://pymupdf.readthedocs.io/) — PDF parsing
* [python-docx](https://python-docx.readthedocs.io/) — DOCX parsing
* [icalendar](https://icalendar.readthedocs.io/) — ICS calendar parsing
* [desktop-notifier](https://github.com/samschott/desktop-notifier) — Cross-platform notifications
* [spaCy](https://spacy.io/) — Named entity recognition
* [YOLO](https://github.com/ultralytics/ultralytics) — Object detection

---

**SafeClaw** — Because your assistant shouldn't cost more than your rent. 🐾
