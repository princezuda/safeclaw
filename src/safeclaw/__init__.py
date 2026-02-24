"""
SafeClaw - A privacy-first personal automation assistant.

No GenAI required for core features. Optional AI blogging with 11 providers.
100% self-hosted. Your data stays yours.
"""

__version__ = "0.2.2"
__author__ = "SafeClaw Contributors"

from safeclaw.core.engine import SafeClaw
from safeclaw.core.memory import Memory
from safeclaw.core.parser import CommandParser

__all__ = ["SafeClaw", "CommandParser", "Memory", "__version__"]
