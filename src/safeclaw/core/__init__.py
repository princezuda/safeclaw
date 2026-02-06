"""Core SafeClaw components."""

from safeclaw.core.analyzer import TextAnalyzer
from safeclaw.core.documents import DocumentReader
from safeclaw.core.engine import SafeClaw
from safeclaw.core.memory import Memory
from safeclaw.core.notifications import NotificationManager
from safeclaw.core.parser import CommandParser
from safeclaw.core.scheduler import Scheduler

__all__ = [
    "SafeClaw",
    "CommandParser",
    "Memory",
    "Scheduler",
    "TextAnalyzer",
    "DocumentReader",
    "NotificationManager",
]

# Optional ML imports (heavy dependencies)
try:
    from safeclaw.core.nlp import NLPProcessor
    __all__.append("NLPProcessor")
except ImportError:
    pass  # pip install safeclaw[nlp]

try:
    from safeclaw.core.vision import ObjectDetector, OCRProcessor, VisionProcessor
    __all__.extend(["VisionProcessor", "ObjectDetector", "OCRProcessor"])
except ImportError:
    pass  # pip install safeclaw[vision]
