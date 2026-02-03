"""
SafeClaw Command Parser - Rule-based intent classification.

No GenAI needed! Uses:
- Keyword matching
- Regex patterns
- Slot filling (dates, times, entities)
- Fuzzy matching for typo tolerance
- User-learned patterns from corrections
"""

import re
import logging
from dataclasses import dataclass, field
from typing import Any, Optional, TYPE_CHECKING
from datetime import datetime

import dateparser
from rapidfuzz import fuzz, process

if TYPE_CHECKING:
    from safeclaw.core.memory import Memory

logger = logging.getLogger(__name__)


# Common phrase variations that map to core intents
# These cover natural language that users might type day-one
PHRASE_VARIATIONS = {
    "reminder": [
        "don't let me forget",
        "make sure i",
        "ping me",
        "tell me to",
        "remind me about",
        "i need to remember",
        "can you remind",
        "heads up about",
        "don't forget to",
        "note to self",
    ],
    "weather": [
        "how's the weather",
        "what's it like outside",
        "is it raining",
        "should i bring umbrella",
        "do i need a jacket",
        "temperature outside",
        "how hot is it",
        "how cold is it",
        "weather check",
    ],
    "crawl": [
        "what links are on",
        "show me links from",
        "find urls on",
        "list links on",
        "what pages link to",
        "scan website",
        "spider",
        "follow links",
    ],
    "email": [
        "any new mail",
        "new messages",
        "did i get mail",
        "any emails",
        "message from",
        "write email",
        "compose email",
        "mail to",
    ],
    "calendar": [
        "what's happening",
        "am i busy",
        "do i have anything",
        "free time",
        "book a meeting",
        "set up meeting",
        "schedule with",
        "my day",
        "today's events",
    ],
    "news": [
        "what's new",
        "latest news",
        "what's going on",
        "current events",
        "top stories",
        "breaking news",
        "recent news",
    ],
    "briefing": [
        "catch me up",
        "what's happening today",
        "daily digest",
        "morning summary",
        "start my day",
        "anything i should know",
        "overview for today",
    ],
    "help": [
        "what do you do",
        "how does this work",
        "show options",
        "list features",
        "what are my options",
        "menu",
        "capabilities",
    ],
    "summarize": [
        "sum up",
        "quick summary",
        "give me the gist",
        "main points",
        "key takeaways",
        "in brief",
        "cliff notes",
        "the short version",
    ],
    "shell": [
        "terminal",
        "cmd",
        "cli",
        "bash",
        "run this",
        "exec",
    ],
    "smarthome": [
        "switch on",
        "switch off",
        "lights on",
        "lights off",
        "make it brighter",
        "make it darker",
        "adjust lights",
    ],
}


# Patterns for detecting command chains
# Order matters - more specific patterns first
CHAIN_PATTERNS = [
    (r'\s*\|\s*', 'pipe'),              # Unix-style pipe: "crawl url | summarize"
    (r'\s*->\s*', 'pipe'),              # Arrow pipe: "crawl url -> summarize"
    (r'\s+and\s+then\s+', 'sequence'),  # "crawl url and then summarize" (must be before "then")
    (r'\s+then\s+', 'sequence'),        # "crawl url then summarize"
    (r'\s*;\s*', 'sequence'),           # Semicolon: "crawl url; summarize"
]


@dataclass
class ParsedCommand:
    """Result of parsing a user command."""
    raw_text: str
    intent: Optional[str] = None
    confidence: float = 0.0
    params: dict[str, Any] = field(default_factory=dict)
    entities: dict[str, Any] = field(default_factory=dict)
    # For command chaining
    chain_type: Optional[str] = None  # 'pipe' or 'sequence' or None
    use_previous_output: bool = False  # True if this command should receive previous output


@dataclass
class CommandChain:
    """A chain of commands to execute in sequence."""
    commands: list[ParsedCommand]
    chain_type: str = "sequence"  # 'pipe' passes output, 'sequence' runs independently


@dataclass
class IntentPattern:
    """Pattern definition for an intent."""
    intent: str
    keywords: list[str]
    patterns: list[str]
    examples: list[str]
    slots: list[str] = field(default_factory=list)


class CommandParser:
    """
    Rule-based command parser with fuzzy matching.

    Parses user input into structured commands without any AI/ML.
    Uses keyword matching, regex, and dateparser for slot filling.
    Supports user-learned patterns from corrections.
    """

    def __init__(self, memory: Optional["Memory"] = None):
        self.intents: dict[str, IntentPattern] = {}
        self.memory = memory
        self._learned_patterns_cache: dict[str, list[dict]] = {}
        self._setup_default_intents()

    def _setup_default_intents(self) -> None:
        """Register default intent patterns."""
        default_intents = [
            IntentPattern(
                intent="reminder",
                keywords=["remind", "reminder", "remember", "alert", "notify"],
                patterns=[
                    r"remind(?:\s+me)?\s+(?:to\s+)?(.+?)(?:\s+(?:at|on|in)\s+(.+))?$",
                    r"set\s+(?:a\s+)?reminder\s+(?:for\s+)?(.+?)(?:\s+(?:at|on|in)\s+(.+))?$",
                ],
                examples=[
                    "remind me to call mom tomorrow at 3pm",
                    "set a reminder for meeting in 2 hours",
                ],
                slots=["task", "time"],
            ),
            IntentPattern(
                intent="weather",
                keywords=["weather", "temperature", "forecast", "rain", "sunny", "cold", "hot"],
                patterns=[
                    r"(?:what(?:'s| is)\s+the\s+)?weather\s+(?:in\s+)?(.+)?",
                    r"(?:is\s+it|will\s+it)\s+(?:going\s+to\s+)?(?:rain|snow|be\s+\w+)\s*(?:in\s+)?(.+)?",
                ],
                examples=[
                    "what's the weather in NYC",
                    "weather tomorrow",
                    "is it going to rain",
                ],
                slots=["location", "time"],
            ),
            IntentPattern(
                intent="summarize",
                keywords=["summarize", "summary", "tldr", "brief", "condense"],
                patterns=[
                    r"summarize\s+(.+)",
                    r"(?:give\s+me\s+)?(?:a\s+)?summary\s+of\s+(.+)",
                    r"tldr\s+(.+)",
                ],
                examples=[
                    "summarize https://example.com/article",
                    "give me a summary of this page",
                    "tldr https://news.com/story",
                ],
                slots=["target"],
            ),
            IntentPattern(
                intent="crawl",
                keywords=["crawl", "scrape", "fetch", "grab", "extract", "get links"],
                patterns=[
                    r"crawl\s+(.+)",
                    r"(?:scrape|fetch|grab)\s+(?:links\s+from\s+)?(.+)",
                    r"get\s+(?:all\s+)?links\s+from\s+(.+)",
                    r"extract\s+(?:urls|links)\s+from\s+(.+)",
                ],
                examples=[
                    "crawl https://example.com",
                    "get links from https://news.site.com",
                    "scrape https://blog.com",
                ],
                slots=["url", "depth"],
            ),
            IntentPattern(
                intent="email",
                keywords=["email", "mail", "inbox", "unread", "send email"],
                patterns=[
                    r"(?:check|show|list)\s+(?:my\s+)?(?:unread\s+)?emails?",
                    r"send\s+(?:an?\s+)?email\s+to\s+(.+)",
                    r"(?:what(?:'s| is)\s+in\s+)?my\s+inbox",
                ],
                examples=[
                    "check my email",
                    "show unread emails",
                    "send email to john@example.com",
                ],
                slots=["recipient", "subject", "body"],
            ),
            IntentPattern(
                intent="calendar",
                keywords=["calendar", "schedule", "meeting", "event", "appointment"],
                patterns=[
                    r"(?:show|what(?:'s| is))\s+(?:on\s+)?my\s+(?:calendar|schedule)",
                    r"(?:add|create|schedule)\s+(?:a\s+)?(?:meeting|event|appointment)\s+(.+)",
                    r"(?:what(?:'s| is)|do\s+i\s+have)\s+(?:happening\s+)?(?:on\s+)?(.+)",
                ],
                examples=[
                    "what's on my calendar",
                    "show my schedule for tomorrow",
                    "add meeting with Bob at 2pm",
                ],
                slots=["action", "event", "time"],
            ),
            IntentPattern(
                intent="shell",
                keywords=["run", "execute", "shell", "command", "terminal"],
                patterns=[
                    r"run\s+(?:command\s+)?[`'\"]?(.+?)[`'\"]?$",
                    r"execute\s+[`'\"]?(.+?)[`'\"]?$",
                    r"shell\s+[`'\"]?(.+?)[`'\"]?$",
                ],
                examples=[
                    "run ls -la",
                    "execute 'git status'",
                    "shell df -h",
                ],
                slots=["command"],
            ),
            IntentPattern(
                intent="files",
                keywords=["file", "files", "folder", "directory", "list", "find", "search"],
                patterns=[
                    r"(?:list|show)\s+files\s+in\s+(.+)",
                    r"find\s+(?:files?\s+)?(.+?)(?:\s+in\s+(.+))?",
                    r"search\s+(?:for\s+)?(.+?)(?:\s+in\s+(.+))?",
                ],
                examples=[
                    "list files in ~/Documents",
                    "find *.py in ~/projects",
                    "search for config files",
                ],
                slots=["pattern", "path"],
            ),
            IntentPattern(
                intent="smarthome",
                keywords=["light", "lights", "lamp", "turn on", "turn off", "dim", "bright"],
                patterns=[
                    r"turn\s+(on|off)\s+(?:the\s+)?(.+?)(?:\s+lights?)?$",
                    r"(?:set|dim)\s+(?:the\s+)?(.+?)\s+(?:lights?\s+)?(?:to\s+)?(\d+)%?",
                    r"(?:make\s+)?(?:the\s+)?(.+?)\s+(brighter|dimmer)",
                ],
                examples=[
                    "turn on living room lights",
                    "turn off bedroom",
                    "dim kitchen to 50%",
                ],
                slots=["action", "room", "level"],
            ),
            IntentPattern(
                intent="briefing",
                keywords=["briefing", "brief", "morning", "daily", "update"],
                patterns=[
                    r"(?:morning|daily|evening)\s+briefing",
                    r"(?:give\s+me\s+)?(?:my\s+)?(?:daily\s+)?(?:briefing|update|summary)",
                    r"what(?:'s| did i)\s+miss",
                ],
                examples=[
                    "morning briefing",
                    "give me my daily update",
                    "what did I miss",
                ],
                slots=[],
            ),
            IntentPattern(
                intent="help",
                keywords=["help", "commands", "what can you do", "how to"],
                patterns=[
                    r"^help$",
                    r"(?:show\s+)?(?:available\s+)?commands",
                    r"what\s+can\s+you\s+do",
                ],
                examples=[
                    "help",
                    "show commands",
                    "what can you do",
                ],
                slots=[],
            ),
            IntentPattern(
                intent="webhook",
                keywords=["webhook", "hook", "trigger", "api"],
                patterns=[
                    r"(?:create|add|set\s+up)\s+(?:a\s+)?webhook\s+(?:for\s+)?(.+)",
                    r"(?:list|show)\s+webhooks",
                    r"trigger\s+webhook\s+(.+)",
                ],
                examples=[
                    "create a webhook for deployments",
                    "list webhooks",
                    "trigger webhook build",
                ],
                slots=["name", "url", "action"],
            ),
            IntentPattern(
                intent="news",
                keywords=["news", "headlines", "feed", "feeds", "rss"],
                patterns=[
                    r"^news$",
                    r"(?:show|get|fetch)\s+(?:me\s+)?(?:the\s+)?news",
                    r"(?:show|get|fetch)\s+(?:me\s+)?(?:the\s+)?headlines",
                    r"news\s+(?:from\s+)?(\w+)",  # news tech, news world
                    r"(?:show|list)\s+(?:news\s+)?(?:categories|feeds)",
                    r"news\s+enable\s+(\w+)",
                    r"news\s+disable\s+(\w+)",
                    r"news\s+add\s+(.+)",
                    r"(?:add|import)\s+(?:rss\s+)?feed\s+(.+)",
                    r"news\s+remove\s+(.+)",
                    r"read\s+(?:article\s+)?(.+)",
                ],
                examples=[
                    "news",
                    "show me the headlines",
                    "news tech",
                    "news categories",
                    "news enable science",
                    "add feed https://blog.example.com/rss",
                    "read https://article.com/story",
                ],
                slots=["category", "subcommand", "url", "target"],
            ),
            IntentPattern(
                intent="analyze",
                keywords=["analyze", "sentiment", "keywords", "readability", "tone"],
                patterns=[
                    r"analyze\s+(?:sentiment\s+)?(?:of\s+)?(.+)",
                    r"(?:what(?:'s| is)\s+the\s+)?sentiment\s+(?:of\s+)?(.+)",
                    r"(?:extract|get)\s+keywords\s+(?:from\s+)?(.+)",
                    r"(?:check|measure)\s+readability\s+(?:of\s+)?(.+)",
                ],
                examples=[
                    "analyze sentiment of this text",
                    "what's the sentiment of this article",
                    "extract keywords from document.txt",
                    "check readability of my essay",
                ],
                slots=["target", "type"],
            ),
            IntentPattern(
                intent="document",
                keywords=["document", "pdf", "docx", "read file", "extract text"],
                patterns=[
                    r"(?:read|open|extract)\s+(?:text\s+from\s+)?(?:document\s+)?(.+\.(?:pdf|docx?|txt|md|html?))",
                    r"(?:what(?:'s| is)\s+in\s+)?(.+\.(?:pdf|docx?|txt|md|html?))",
                    r"summarize\s+(?:document\s+)?(.+\.(?:pdf|docx?))",
                ],
                examples=[
                    "read document.pdf",
                    "extract text from report.docx",
                    "what's in notes.txt",
                    "summarize paper.pdf",
                ],
                slots=["path"],
            ),
            IntentPattern(
                intent="notify",
                keywords=["notify", "notification", "alert", "desktop"],
                patterns=[
                    r"(?:send\s+)?notification\s+(.+)",
                    r"notify\s+(?:me\s+)?(?:that\s+)?(.+)",
                    r"(?:show\s+)?(?:notification\s+)?history",
                ],
                examples=[
                    "send notification Task complete",
                    "notify me that the build finished",
                    "notification history",
                ],
                slots=["message", "priority"],
            ),
            IntentPattern(
                intent="vision",
                keywords=["detect", "objects", "what's in", "identify", "yolo", "image"],
                patterns=[
                    r"(?:detect|find|identify)\s+(?:objects\s+)?(?:in\s+)?(.+\.(?:jpg|jpeg|png|gif|webp))",
                    r"what(?:'s| is)\s+in\s+(?:this\s+)?(?:image|photo|picture)\s*(.+)?",
                    r"(?:analyze|describe)\s+(?:this\s+)?(?:image|photo)\s*(.+)?",
                ],
                examples=[
                    "detect objects in photo.jpg",
                    "what's in this image",
                    "identify objects in screenshot.png",
                ],
                slots=["path"],
            ),
            IntentPattern(
                intent="ocr",
                keywords=["ocr", "extract text", "read text", "scan"],
                patterns=[
                    r"(?:ocr|scan|extract\s+text)\s+(?:from\s+)?(.+\.(?:jpg|jpeg|png|gif|webp|pdf))",
                    r"(?:read|get)\s+text\s+from\s+(?:image\s+)?(.+)",
                    r"what\s+(?:does|do)\s+(?:it|this)\s+say",
                ],
                examples=[
                    "ocr photo.jpg",
                    "extract text from screenshot.png",
                    "read text from receipt.jpg",
                ],
                slots=["path"],
            ),
            IntentPattern(
                intent="entities",
                keywords=["entities", "ner", "people", "places", "organizations", "extract names"],
                patterns=[
                    r"(?:extract|find|get)\s+(?:named\s+)?entities\s+(?:from\s+)?(.+)",
                    r"(?:who|what)\s+(?:people|organizations?|places?|locations?)\s+(?:are\s+)?(?:in|mentioned)\s+(.+)",
                    r"ner\s+(.+)",
                ],
                examples=[
                    "extract entities from article.txt",
                    "find people mentioned in document.pdf",
                    "what organizations are in this text",
                ],
                slots=["target"],
            ),
        ]

        for intent in default_intents:
            self.register_intent(intent)

    def register_intent(self, pattern: IntentPattern) -> None:
        """Register a new intent pattern."""
        self.intents[pattern.intent] = pattern
        logger.debug(f"Registered intent: {pattern.intent}")

    def parse(self, text: str, user_id: Optional[str] = None) -> ParsedCommand:
        """
        Parse user input into a structured command.

        Returns ParsedCommand with intent, confidence, and extracted params.

        Args:
            text: User input to parse
            user_id: Optional user ID for checking learned patterns
        """
        text = text.strip()
        result = ParsedCommand(raw_text=text)

        if not text:
            return result

        # Normalize text
        normalized = text.lower()

        # 1. Check learned patterns first (user corrections have highest priority)
        if user_id and user_id in self._learned_patterns_cache:
            learned_match = self._match_learned_patterns(normalized, user_id)
            if learned_match:
                result.intent = learned_match["intent"]
                result.confidence = 0.98  # Very high - user explicitly corrected this
                result.params = learned_match.get("params") or {}
                result.entities = self._extract_entities(text)
                logger.debug(f"Matched learned pattern: '{text}' -> {result.intent}")
                return result

        # 2. Check phrase variations (fuzzy match against common phrases)
        phrase_match = self._match_phrase_variations(normalized)
        if phrase_match and phrase_match[1] >= 0.85:
            result.intent = phrase_match[0]
            result.confidence = phrase_match[1]

            intent_pattern = self.intents[result.intent]
            result.params = self._extract_params(text, intent_pattern)
            result.entities = self._extract_entities(text)
            return result

        # 3. Fall back to keyword/pattern matching
        best_match = self._match_keywords(normalized)

        if best_match:
            result.intent = best_match[0]
            result.confidence = best_match[1]

            # Extract params using regex patterns
            intent_pattern = self.intents[result.intent]
            result.params = self._extract_params(text, intent_pattern)
            result.entities = self._extract_entities(text)

        return result

    def _match_keywords(self, text: str) -> Optional[tuple[str, float]]:
        """Match text against intent keywords using fuzzy matching."""
        best_intent = None
        best_score = 0.0

        words = text.split()

        for intent_name, pattern in self.intents.items():
            # Check for keyword matches
            for keyword in pattern.keywords:
                # Exact match in text
                if keyword in text:
                    score = 0.9
                    if score > best_score:
                        best_score = score
                        best_intent = intent_name
                    continue

                # Fuzzy match against words
                for word in words:
                    ratio = fuzz.ratio(keyword, word) / 100.0
                    if ratio > 0.8 and ratio > best_score:
                        best_score = ratio
                        best_intent = intent_name

            # Check regex patterns
            for regex in pattern.patterns:
                if re.search(regex, text, re.IGNORECASE):
                    score = 0.95
                    if score > best_score:
                        best_score = score
                        best_intent = intent_name

        if best_intent and best_score >= 0.6:
            return (best_intent, best_score)

        return None

    def _extract_params(self, text: str, pattern: IntentPattern) -> dict[str, Any]:
        """Extract parameters from text using regex patterns."""
        params: dict[str, Any] = {}

        for regex in pattern.patterns:
            match = re.search(regex, text, re.IGNORECASE)
            if match:
                groups = match.groups()
                # Map groups to slots
                for i, slot in enumerate(pattern.slots):
                    if i < len(groups) and groups[i]:
                        params[slot] = groups[i].strip()
                break

        return params

    def _extract_entities(self, text: str) -> dict[str, Any]:
        """Extract common entities (dates, times, URLs, emails)."""
        entities: dict[str, Any] = {}

        # Extract URLs
        url_pattern = r'https?://[^\s<>"{}|\\^`\[\]]+'
        urls = re.findall(url_pattern, text)
        if urls:
            entities["urls"] = urls

        # Extract emails
        email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        emails = re.findall(email_pattern, text)
        if emails:
            entities["emails"] = emails

        # Extract dates/times using dateparser
        # Remove URLs first to avoid confusion
        text_no_urls = re.sub(url_pattern, '', text)
        parsed_date = dateparser.parse(
            text_no_urls,
            settings={
                'PREFER_DATES_FROM': 'future',
                'RELATIVE_BASE': datetime.now(),
            }
        )
        if parsed_date:
            entities["datetime"] = parsed_date

        # Extract numbers
        numbers = re.findall(r'\b(\d+(?:\.\d+)?)\b', text)
        if numbers:
            entities["numbers"] = [float(n) if '.' in n else int(n) for n in numbers]

        return entities

    def get_intents(self) -> list[str]:
        """Return list of registered intent names."""
        return list(self.intents.keys())

    def get_examples(self, intent: str) -> list[str]:
        """Return example phrases for an intent."""
        if intent in self.intents:
            return self.intents[intent].examples
        return []

    def _match_phrase_variations(self, text: str) -> Optional[tuple[str, float]]:
        """
        Match text against common phrase variations using fuzzy matching.

        This provides day-one natural language understanding without training.
        """
        best_intent = None
        best_score = 0.0

        for intent, phrases in PHRASE_VARIATIONS.items():
            if intent not in self.intents:
                continue

            for phrase in phrases:
                # Check if phrase is contained in text
                if phrase in text:
                    score = 0.92
                    if score > best_score:
                        best_score = score
                        best_intent = intent
                    continue

                # Fuzzy match - check if any part of text matches phrase
                # Use partial_ratio for substring matching
                ratio = fuzz.partial_ratio(phrase, text) / 100.0
                if ratio > 0.85 and ratio > best_score:
                    best_score = ratio
                    best_intent = intent

        if best_intent and best_score >= 0.85:
            return (best_intent, best_score)

        return None

    def _match_learned_patterns(
        self, text: str, user_id: str
    ) -> Optional[dict[str, Any]]:
        """
        Match text against user's learned patterns using fuzzy matching.

        Returns the best matching pattern if found with high confidence.
        """
        if user_id not in self._learned_patterns_cache:
            return None

        patterns = self._learned_patterns_cache[user_id]
        if not patterns:
            return None

        best_match = None
        best_score = 0.0

        for pattern in patterns:
            phrase = pattern["phrase"]

            # Exact match (normalized)
            if text == phrase:
                return pattern

            # Fuzzy match - higher threshold for learned patterns
            ratio = fuzz.ratio(phrase, text) / 100.0
            if ratio > 0.90 and ratio > best_score:
                best_score = ratio
                best_match = pattern

        return best_match

    async def load_user_patterns(self, user_id: str) -> None:
        """
        Load learned patterns for a user from memory.

        Call this when a user session starts to enable learned pattern matching.
        """
        if not self.memory:
            return

        patterns = await self.memory.get_user_patterns(user_id)
        self._learned_patterns_cache[user_id] = patterns
        logger.debug(f"Loaded {len(patterns)} learned patterns for user {user_id}")

    async def learn_correction(
        self,
        user_id: str,
        phrase: str,
        correct_intent: str,
        params: Optional[dict] = None,
    ) -> None:
        """
        Learn a correction from user feedback.

        When a user says "I meant X" or corrects a misunderstood command,
        store the mapping so future similar phrases match correctly.

        Args:
            user_id: User who made the correction
            phrase: The original phrase that was misunderstood
            correct_intent: The intent the user actually wanted
            params: Optional parameters for the intent
        """
        if not self.memory:
            logger.warning("Cannot learn correction: no memory configured")
            return

        # Store in database
        await self.memory.learn_pattern(user_id, phrase, correct_intent, params)

        # Update cache
        if user_id not in self._learned_patterns_cache:
            self._learned_patterns_cache[user_id] = []

        # Check if already in cache and update, or add new
        normalized = phrase.lower().strip()
        for existing in self._learned_patterns_cache[user_id]:
            if existing["phrase"] == normalized:
                existing["intent"] = correct_intent
                existing["params"] = params
                existing["use_count"] = existing.get("use_count", 0) + 1
                logger.info(f"Updated learned pattern: '{phrase}' -> {correct_intent}")
                return

        # Add new pattern to cache
        self._learned_patterns_cache[user_id].append({
            "phrase": normalized,
            "intent": correct_intent,
            "params": params,
            "use_count": 1,
        })
        logger.info(f"Learned new pattern: '{phrase}' -> {correct_intent}")

    def _detect_chain(self, text: str) -> Optional[tuple[str, str]]:
        """
        Detect if text contains a command chain pattern.

        Returns tuple of (pattern, chain_type) or None if no chain detected.
        """
        for pattern, chain_type in CHAIN_PATTERNS:
            if re.search(pattern, text, re.IGNORECASE):
                return (pattern, chain_type)
        return None

    def _split_chain(self, text: str) -> tuple[list[str], str]:
        """
        Split text into chain segments.

        Returns tuple of (segments, chain_type).
        """
        # Try each pattern in order
        for pattern, chain_type in CHAIN_PATTERNS:
            parts = re.split(pattern, text, flags=re.IGNORECASE)
            if len(parts) > 1:
                # Clean up parts and filter empty ones
                segments = [p.strip() for p in parts if p.strip()]
                if len(segments) > 1:
                    return (segments, chain_type)

        # No chain found - return single segment
        return ([text], "none")

    def parse_chain(
        self, text: str, user_id: Optional[str] = None
    ) -> CommandChain:
        """
        Parse a potentially chained command.

        Supports:
        - Pipes: "crawl url | summarize" - passes output to next command
        - Arrows: "crawl url -> summarize" - same as pipe
        - Sequence: "check email; remind me to reply" - runs independently
        - Natural: "crawl url and then summarize it" - contextual chaining

        Args:
            text: User input that may contain multiple chained commands
            user_id: Optional user ID for learned pattern matching

        Returns:
            CommandChain with list of ParsedCommands
        """
        text = text.strip()

        # Split into segments
        segments, chain_type = self._split_chain(text)

        if len(segments) == 1:
            # Single command - no chaining
            cmd = self.parse(text, user_id)
            return CommandChain(commands=[cmd], chain_type="none")

        # Parse each segment
        commands: list[ParsedCommand] = []
        for i, segment in enumerate(segments):
            cmd = self.parse(segment, user_id)

            # Mark chain info
            cmd.chain_type = chain_type if i < len(segments) - 1 else None

            # For pipes, subsequent commands use previous output
            if chain_type == "pipe" and i > 0:
                cmd.use_previous_output = True
                # Handle implicit targets like "summarize it", "summarize that"
                if not cmd.params.get("target") and not cmd.entities.get("urls"):
                    cmd.params["_use_previous"] = True

            commands.append(cmd)

        logger.debug(f"Parsed chain with {len(commands)} commands ({chain_type})")
        return CommandChain(commands=commands, chain_type=chain_type)

    def is_chain(self, text: str) -> bool:
        """Check if text contains a command chain."""
        return self._detect_chain(text) is not None
