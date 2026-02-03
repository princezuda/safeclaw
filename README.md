# SafeClaw 🐾

**Privacy-first personal automation assistant - no GenAI required.**

SafeClaw is an open-source alternative to cloud-based AI assistants that runs entirely on your machine. It does 90% of what Clawdbot/OpenClaw does using traditional programming - rule-based parsing, webhooks, web crawling, and extractive summarization.

## Features

### 🔒 Privacy First
- **100% self-hosted** - Your data never leaves your machine
- **No API keys required** - Works completely offline
- **No cloud dependencies** - Everything runs locally

### 🤖 No GenAI Required
- **Rule-based command parsing** - Keyword matching, regex, fuzzy search
- **Extractive summarization** - Uses [sumy](https://github.com/miso-belica/sumy) (LSA, LexRank, TextRank)
- **Pattern matching** - dateparser for natural language dates

### 📡 Multi-Channel
- **CLI** - Interactive command line interface
- **Telegram** - Bot integration
- **Discord** - (coming soon)
- **Slack** - (coming soon)
- **Webhooks** - Inbound/outbound webhook support

### 📰 RSS News Aggregation
- **Preset categories** - Tech, World, Science, Business, Programming, Security, Linux, AI
- **50+ feeds included** - Hacker News, Ars Technica, BBC, Reuters, Nature, and more
- **Custom feeds** - Import your own RSS/Atom feeds
- **Auto-summarization** - Summarize articles with sumy (no AI!)
- **Per-user preferences** - Each user can customize their news sources

### ⚡ Automation
- **Web crawling** - Extract links and content from websites
- **Summarization** - Summarize articles without AI
- **Reminders** - Natural language time parsing
- **Shell commands** - Sandboxed command execution
- **File operations** - Search, list, read files
- **Cron jobs** - Scheduled tasks
- **Daily briefings** - Weather, reminders, news from your RSS feeds

### 📊 Text Analysis (No ML!)
- **VADER Sentiment** - Lexicon-based sentiment analysis
- **Keyword Extraction** - TF-IDF style extraction
- **Readability Scoring** - Flesch-Kincaid metrics

### 📧 Email Integration
- **IMAP Support** - Read emails from Gmail, Outlook, Yahoo
- **SMTP Support** - Send emails
- **Standard Protocols** - No API keys required

### 📅 Calendar Support
- **ICS Files** - Import and parse .ics calendar files
- **CalDAV** - Connect to Google Calendar, iCloud (optional)
- **Event Filtering** - Today, upcoming, by date range

### 📄 Document Reading
- **PDF** - Extract text with PyMuPDF
- **DOCX** - Microsoft Word documents
- **HTML/Markdown/TXT** - Plain text formats

### 🔔 Notifications
- **Desktop Notifications** - Cross-platform (macOS, Windows, Linux)
- **Priority Levels** - Low, normal, high, urgent
- **Rate Limiting** - Prevent notification spam

## Installation

### Using pipx (recommended for most users)

```bash
# Install pipx if needed
sudo apt install pipx
pipx ensurepath

# Install SafeClaw
pipx install safeclaw
```

### Using pip with virtual environment

Modern Linux distros require virtual environments:

```bash
# Create and activate venv
python3 -m venv ~/.safeclaw-venv
source ~/.safeclaw-venv/bin/activate

# Install SafeClaw
pip install safeclaw
```

### From source

```bash
git clone https://github.com/safeclaw/safeclaw.git
cd safeclaw
pip install -e .
```

### Optional ML Features

For users with more disk space:

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

**Requirements:** Python 3.11+, ~50MB disk (base), ~2GB additional for vision features

## Quick Start

### Interactive CLI

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
> calendar today                    # Today's events from .ics
> analyze sentiment of this text    # VADER sentiment analysis
> read document.pdf                 # Extract text from documents
> help
```

### CLI Commands

```bash
# Get news headlines
safeclaw news                       # From enabled categories
safeclaw news tech                  # Tech news only
safeclaw news --categories          # List all categories
safeclaw news world -n 20           # 20 world news headlines
safeclaw news --add https://blog.example.com/rss --name "My Blog"
safeclaw news -s                    # With summaries

# Summarize a URL
safeclaw summarize https://example.com/article -n 5

# Crawl a website
safeclaw crawl https://example.com --depth 2

# Analyze text (sentiment, keywords, readability)
safeclaw analyze "This product is amazing! I love it."
safeclaw analyze document.txt --no-readability

# Read documents (PDF, DOCX, TXT, MD, HTML)
safeclaw document report.pdf
safeclaw document paper.docx --summarize -n 5
safeclaw document notes.md --output extracted.txt

# Calendar (ICS files)
safeclaw calendar import --file calendar.ics
safeclaw calendar today
safeclaw calendar upcoming --days 14

# Start webhook server
safeclaw webhook --port 8765

# Initialize config
safeclaw init
```

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
  weather:
    enabled: true
    provider: "wttr"  # or "open-meteo" - both free, no API key!
    units: "imperial"  # or "metric"
    default_location: "New York"
```

### Weather (No API Key Needed)

SafeClaw uses **[wttr.in](https://wttr.in)** for weather - a free service that requires no API key:

```
> weather
> weather in Paris
> what's the weather in Tokyo
```

**Alternative: Open-Meteo** (also free, no key):
Add to config (`~/.safeclaw/config.yaml`) if you prefer Open-Meteo:
```yaml
actions:
  weather:
    enabled: true
    provider: "open-meteo"  # or "wttr" (default)
    units: "imperial"  # or "metric" for Celsius
    default_location: "New York"
```

Both options:
- ✅ 100% free
- ✅ No API key required
- ✅ No sign-up needed

### Command Chaining

Chain multiple commands together using pipes or sequences:

**Pipes** - Pass output from one command to the next:
```
> crawl https://example.com | summarize
> crawl site.com -> summarize it -> email to me
```

**Sequences** - Run commands independently:
```
> check email; remind me to reply
> news and then weather
> crawl site.com then summarize
```

Supported chain operators:
- `|` or `->` - Pipe (passes output)
- `;` - Sequence (independent)
- `and then` / `then` - Natural language sequence

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
│                   │ • News/RSS  │                   └────────────┘  │
│                   │ • Email     │                                    │
│                   │ • Calendar  │                                    │
│                   └─────────────┘                                    │
│                                                                      │
│  ┌───────────────────────────────────────────────────────────┐      │
│  │                  COMMAND PARSER                            │      │
│  │   Keyword + Regex + Fuzzy Match + Date Parser + NLP       │      │
│  └───────────────────────────────────────────────────────────┘      │
│                                                                      │
│  ┌───────────────────────────────────────────────────────────┐      │
│  │                  MEMORY (SQLite)                           │      │
│  │   History • Preferences • Reminders • Cache • Events      │      │
│  └───────────────────────────────────────────────────────────┘      │
└──────────────────────────────────────────────────────────────────────┘
```

## How It Works (No AI!)

### Command Parsing
Instead of using LLMs to understand commands, SafeClaw uses:

1. **Keyword matching** - Fast lookup of command keywords
2. **Regex patterns** - Structured extraction of parameters
3. **Fuzzy matching** - Typo tolerance with rapidfuzz
4. **Date parsing** - Natural language dates with dateparser

```python
# Example: "remind me to call mom tomorrow at 3pm"
# → intent: "reminder"
# → params: {task: "call mom", time: "tomorrow at 3pm"}
# → entities: {datetime: 2024-01-16 15:00:00}
```

### Summarization
Uses [sumy](https://github.com/miso-belica/sumy)'s extractive algorithms:

- **LexRank** - Graph-based, like PageRank for sentences
- **TextRank** - Word co-occurrence graphs
- **LSA** - Latent Semantic Analysis
- **Luhn** - Statistical word frequency

No neural networks, no API calls - pure math!

### Web Crawling
Async crawling with httpx + BeautifulSoup:

- Single page link extraction
- Multi-page crawling with depth limits
- Domain filtering
- Pattern matching
- Built-in caching

### RSS News Aggregation
Fetch news from 50+ preset feeds or add your own:

```bash
# Available categories
safeclaw news --categories

📂 Available News Categories

✅ tech (6 feeds)
   • Hacker News
   • Ars Technica
   • The Verge
   • ... and 3 more

⬜ world (5 feeds)
   • BBC World
   • Reuters World
   • Al Jazeera
   • ... and 2 more

⬜ science (5 feeds)
⬜ business (4 feeds)
⬜ programming (5 feeds)
⬜ security (4 feeds)
⬜ linux (4 feeds)
⬜ ai (4 feeds)
```

**Interactive commands:**
```
> news                    # Headlines from enabled categories
> news tech               # Tech news only
> news enable science     # Enable science category
> news disable tech       # Disable tech category
> add feed https://myblog.com/rss   # Add custom feed
> news remove myblog.com  # Remove custom feed
> read https://article.com/story    # Fetch and summarize article
```

**Summarization with news:**
```bash
# Get news with auto-summarization (uses sumy, no AI!)
safeclaw news -s

📰 News Headlines

── TECH ──

**Apple Announces New M4 Chip**
Hacker News • Feb 02, 10:30
The new M4 chip features improved neural engine performance
and 40% better battery efficiency compared to M3.
https://...
```

## Webhooks

SafeClaw can both receive and send webhooks:

### Inbound Webhooks

```bash
# Start webhook server
safeclaw webhook --port 8765

# Webhooks are available at:
# POST http://localhost:8765/webhook/{name}
```

### Configuring Webhooks

```python
from safeclaw.triggers.webhook import WebhookServer

server = WebhookServer(port=8765)
server.register(
    name="github",
    action="shell",
    secret="your-webhook-secret",
)
```

### Outbound Webhooks

```python
from safeclaw.triggers.webhook import WebhookClient

client = WebhookClient()
await client.send_to_slack(
    webhook_url="https://hooks.slack.com/...",
    text="Deployment complete!",
)
```

## Plugins

SafeClaw has a plugin system for extending functionality. Plugins are automatically loaded from:

```
src/safeclaw/plugins/
├── official/      # Curated, tested plugins
│   └── smarthome.py
├── community/     # User-contributed plugins
│   └── your_plugin.py
├── base.py        # BasePlugin class
└── loader.py      # Plugin loader
```

### Official Plugins

| Plugin | Description | Install |
|--------|-------------|---------|
| `smarthome` | Philips Hue & MQTT/Home Assistant | `pip install safeclaw[smarthome]` |

### Creating a Plugin

Create a new `.py` file in `plugins/community/`:

```python
# plugins/community/hello.py
from safeclaw.plugins.base import BasePlugin, PluginInfo

class HelloPlugin(BasePlugin):
    info = PluginInfo(
        name="hello",
        version="1.0.0",
        description="A friendly greeting plugin",
        author="Your Name",
        keywords=["hello", "hi", "greet", "hey"],
        patterns=[r"^hello$", r"^hi\s*(.*)$", r"^hey\s*(.*)$"],
        examples=["hello", "hi there", "hey safeclaw"],
    )

    async def execute(self, params, user_id, channel, engine):
        return "Hello! How can I help you today?"
```

That's it! The plugin is automatically:
- Loaded on startup
- Registered as an action
- Added to the parser with your keywords/patterns

### Plugin API

```python
class BasePlugin(ABC):
    info: PluginInfo  # Required metadata

    async def execute(self, params, user_id, channel, engine) -> str:
        """Main plugin logic. Return response string."""
        pass

    def on_load(self, engine) -> None:
        """Called when plugin loads. Use for initialization."""
        pass

    def on_unload(self) -> None:
        """Called when plugin unloads. Use for cleanup."""
        pass
```

### PluginInfo Fields

| Field | Type | Description |
|-------|------|-------------|
| `name` | str | Unique plugin name (becomes the action name) |
| `version` | str | Semantic version |
| `description` | str | What the plugin does |
| `author` | str | Plugin author |
| `keywords` | list | Words that trigger this plugin |
| `patterns` | list | Regex patterns for matching |
| `examples` | list | Example commands for help text |

### Accessing Engine Features

Plugins have full access to the SafeClaw engine:

```python
async def execute(self, params, user_id, channel, engine):
    # Access config
    my_config = engine.config.get("plugins", {}).get("myplugin", {})

    # Access memory (SQLite)
    await engine.memory.set("key", "value")
    value = await engine.memory.get("key")

    # Access other actions
    # result = await engine.actions["weather"](params={}, user_id=user_id, ...)

    return "Done!"
```

### Contributing Plugins

1. Create your plugin in `plugins/community/`
2. Test it thoroughly
3. Submit a PR to move it to `plugins/official/`

We review plugins for:
- Security (no malicious code)
- Quality (error handling, logging)
- Usefulness (solves a real need)

## Comparison with Clawdbot/OpenClaw

| Feature | SafeClaw | Clawdbot |
|---------|----------|----------|
| Self-hosted | ✅ | ✅ |
| No AI required | ✅ | ❌ |
| Offline capable | ✅ | ❌ |
| Privacy-first | ✅ | ✅ |
| Multi-channel | ✅ | ✅ |
| Web crawling | ✅ | ✅ |
| Summarization | ✅ (extractive) | ✅ (AI) |
| RSS/News feeds | ✅ | ✅ |
| Sentiment analysis | ✅ (VADER) | ✅ (AI) |
| Email integration | ✅ | ✅ |
| Calendar support | ✅ | ✅ |
| Document reading | ✅ | ✅ |
| Desktop notifications | ✅ | ✅ |
| Free-form chat | ❌ | ✅ |
| Creative writing | ❌ | ✅ |

**SafeClaw is for you if:**
- You want automation without AI dependencies
- Privacy is paramount
- You prefer deterministic, predictable behavior
- You don't need free-form conversation
- You want to avoid API costs and rate limits

## Development

```bash
# Clone the repo
git clone https://github.com/safeclaw/safeclaw.git
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

## License

MIT License - see [LICENSE](LICENSE) for details.

## Contributing

Contributions welcome! Please read our contributing guidelines first.

Areas we'd love help with:
- More channel adapters (Discord, Slack, Matrix)
- Smart home integrations (Home Assistant, Philips Hue)
- Better intent patterns
- Documentation improvements
- Tests and CI/CD

## Acknowledgments

- [sumy](https://github.com/miso-belica/sumy) - Extractive summarization
- [VADER](https://github.com/cjhutto/vaderSentiment) - Sentiment analysis
- [feedparser](https://github.com/kurtmckee/feedparser) - RSS/Atom feed parsing
- [dateparser](https://github.com/scrapinghub/dateparser) - Natural language date parsing
- [rapidfuzz](https://github.com/maxbachmann/RapidFuzz) - Fast fuzzy matching
- [httpx](https://github.com/encode/httpx) - Async HTTP client
- [FastAPI](https://fastapi.tiangolo.com/) - Webhook server
- [Rich](https://github.com/Textualize/rich) - Beautiful CLI output
- [PyMuPDF](https://pymupdf.readthedocs.io/) - PDF parsing
- [python-docx](https://python-docx.readthedocs.io/) - DOCX parsing
- [icalendar](https://icalendar.readthedocs.io/) - ICS calendar parsing
- [desktop-notifier](https://github.com/samschott/desktop-notifier) - Cross-platform notifications

---

**SafeClaw** - Because sometimes you just want things to work, predictably. 🐾

