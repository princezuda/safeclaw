# Changelog

All notable changes to SafeClaw will be documented in this file.

Every huge milestone, we add something new. Next milestone: **100 stars.**

---

## [0.2.1] - 2026-02-17

### Added
- **Blog without a language model** (50-star milestone feature)
  - Write blog news with natural language commands
  - Crawl websites for title, body, or non-title content
  - Auto-generate blog titles using extractive summarization — the most repeated, most representative content becomes the headline
  - Publish as plain .txt files
- 50-star celebration banner on CLI startup
- `safeclaw blog` CLI subcommand
- Blog intent patterns in command parser
- Next milestone (100 stars) noted in CLI banner and README

## [0.2.0] - 2026-02-17

### Added
- Social media monitor plugin (Twitter/X via Nitter, Mastodon, Bluesky)

### Fixed
- Ruff linting errors in social monitor plugin

## [0.1.9] - 2026-02-17

### Fixed
- CI: resolved all ruff lint errors
- Added security test suite

## [0.1.8] - 2026-02-17

### Fixed
- Critical security vulnerabilities across multiple modules (SSRF protection, shell sandboxing, crawl redirect validation)

### Added
- macOS support with platform-aware audio handling
- CI configuration

## [0.1.7] - 2026-02-17

### Added
- Device discovery plugin (Bluetooth scanning, network device discovery)

## [0.1.6] - 2026-02-17

### Added
- Easter eggs plugin (love, marriage, valentine responses with animated hearts)
- Piper TTS plugin for local text-to-speech
- Whisper STT plugin for local speech-to-text

## [0.1.5] - 2026-02-17

### Changed
- Removed false claim about LLM/Ollama integration

## [0.1.4] - 2026-02-17

### Added
- Plugin system for extending SafeClaw (official + community plugin directories, auto-loading)

## [0.1.3] - 2026-02-17

### Added
- Weather action using free APIs (no signup required)
- Weather API and command chaining docs in README

### Changed
- Switched to free weather APIs that need no signup

## [0.1.2] - 2026-02-17

### Added
- `__main__.py` for `python -m safeclaw` support
- Natural language understanding with user-learned patterns
- Command chaining with pipes (`|`, `->`) and sequences (`;`, `and then`)

## [0.1.1] - 2026-02-17

### Fixed
- HTTP client closed prematurely in crawl action
- Datetime overflow and HTTP client lifecycle bugs

### Added
- SQLite prepared statements for SQL injection safety
- `.gitignore` for Python artifacts and IDE files

## [0.1.0] - 2026-02-17

### Added
- Initial release of SafeClaw
- Rule-based command parser (keyword, regex, fuzzy matching, dateparser)
- Core actions: files, shell, summarize, crawl, reminder, briefing, news, email, calendar
- Multi-channel support (CLI, Telegram, webhooks)
- SQLite-based memory (history, preferences, reminders, cache)
- RSS news aggregation with 50+ preset feeds across 8 categories
- Extractive summarization (LexRank, TextRank, LSA, Luhn, Edmundson)
- VADER sentiment analysis, keyword extraction, readability scoring
- PDF/DOCX/HTML/Markdown document reading
- Cross-platform desktop notifications
- Scheduler with APScheduler
- Optional NLP (spaCy NER), vision (YOLO), and OCR (Tesseract)
