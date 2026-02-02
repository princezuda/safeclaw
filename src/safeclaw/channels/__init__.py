"""SafeClaw channels - input/output adapters."""

from safeclaw.channels.base import BaseChannel
from safeclaw.channels.cli import CLIChannel

__all__ = ["BaseChannel", "CLIChannel"]
