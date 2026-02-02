"""
SafeClaw Core Engine - The main event loop and orchestrator.

Coordinates channels, actions, triggers, and the command parser.
"""

import asyncio
import logging
from pathlib import Path
from typing import Any, Callable, Optional

import yaml

from safeclaw.core.parser import CommandParser
from safeclaw.core.memory import Memory
from safeclaw.core.scheduler import Scheduler

logger = logging.getLogger(__name__)


class SafeClaw:
    """
    Main SafeClaw engine that orchestrates all components.

    Features:
    - Multi-channel message handling (Telegram, Discord, CLI, etc.)
    - Action execution (files, shell, browser, email, etc.)
    - Scheduled triggers (cron, webhooks, file watchers)
    - Persistent memory (SQLite-based)
    - No GenAI required - uses rule-based parsing
    """

    def __init__(
        self,
        config_path: Optional[Path] = None,
        data_dir: Optional[Path] = None,
    ):
        self.config_path = config_path or Path("config/config.yaml")
        self.data_dir = data_dir or Path.home() / ".safeclaw"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.config: dict[str, Any] = {}
        self.channels: dict[str, Any] = {}
        self.actions: dict[str, Callable] = {}
        self.running = False

        # Core components
        self.parser = CommandParser()
        self.memory = Memory(self.data_dir / "memory.db")
        self.scheduler = Scheduler()

        # Event queue for async message processing
        self._message_queue: asyncio.Queue = asyncio.Queue()

    def load_config(self) -> None:
        """Load configuration from YAML file."""
        if self.config_path.exists():
            with open(self.config_path) as f:
                self.config = yaml.safe_load(f) or {}
            logger.info(f"Loaded config from {self.config_path}")
        else:
            logger.warning(f"Config not found at {self.config_path}, using defaults")
            self.config = self._default_config()

    def _default_config(self) -> dict[str, Any]:
        """Return default configuration."""
        return {
            "safeclaw": {
                "name": "SafeClaw",
                "language": "en",
                "timezone": "UTC",
            },
            "channels": {
                "cli": {"enabled": True},
                "webhook": {"enabled": True, "port": 8765},
            },
            "actions": {
                "shell": {"enabled": True, "sandboxed": True},
                "files": {"enabled": True, "allowed_paths": ["~"]},
                "browser": {"enabled": False},
            },
            "memory": {
                "max_history": 1000,
                "retention_days": 365,
            },
        }

    def register_channel(self, name: str, channel: Any) -> None:
        """Register a communication channel."""
        self.channels[name] = channel
        logger.info(f"Registered channel: {name}")

    def register_action(self, name: str, handler: Callable) -> None:
        """Register an action handler."""
        self.actions[name] = handler
        logger.info(f"Registered action: {name}")

    async def handle_message(
        self,
        text: str,
        channel: str,
        user_id: str,
        metadata: Optional[dict] = None,
    ) -> str:
        """
        Process an incoming message and return a response.

        This is the main entry point for all channels.
        """
        metadata = metadata or {}

        # Parse the command
        parsed = self.parser.parse(text)
        logger.debug(f"Parsed command: {parsed}")

        # Store in memory
        await self.memory.store_message(
            user_id=user_id,
            channel=channel,
            text=text,
            parsed=parsed,
            metadata=metadata,
        )

        # Execute the action
        if parsed.intent and parsed.intent in self.actions:
            try:
                result = await self._execute_action(
                    action=parsed.intent,
                    params=parsed.params,
                    user_id=user_id,
                    channel=channel,
                )
                return result
            except Exception as e:
                logger.error(f"Action failed: {e}")
                return f"Sorry, that action failed: {e}"

        # No matching intent
        if parsed.intent:
            return f"I understand you want to '{parsed.intent}', but I don't have that action configured."

        return "I didn't understand that command. Try 'help' to see what I can do."

    async def _execute_action(
        self,
        action: str,
        params: dict[str, Any],
        user_id: str,
        channel: str,
    ) -> str:
        """Execute a registered action."""
        handler = self.actions[action]

        # Check if handler is async
        if asyncio.iscoroutinefunction(handler):
            return await handler(params=params, user_id=user_id, channel=channel, engine=self)
        else:
            return handler(params=params, user_id=user_id, channel=channel, engine=self)

    async def start(self) -> None:
        """Start the SafeClaw engine."""
        logger.info("Starting SafeClaw...")
        self.running = True

        # Initialize components
        self.load_config()
        await self.memory.initialize()
        await self.scheduler.start()

        # Start all enabled channels
        channel_tasks = []
        for name, channel in self.channels.items():
            if hasattr(channel, "start"):
                channel_tasks.append(asyncio.create_task(channel.start()))
                logger.info(f"Started channel: {name}")

        # Main event loop
        try:
            await asyncio.gather(*channel_tasks)
        except asyncio.CancelledError:
            logger.info("SafeClaw shutting down...")

    async def stop(self) -> None:
        """Stop the SafeClaw engine."""
        logger.info("Stopping SafeClaw...")
        self.running = False

        # Stop scheduler
        await self.scheduler.stop()

        # Stop all channels
        for name, channel in self.channels.items():
            if hasattr(channel, "stop"):
                await channel.stop()
                logger.info(f"Stopped channel: {name}")

        # Close memory connection
        await self.memory.close()

        logger.info("SafeClaw stopped.")

    def get_help(self) -> str:
        """Return help text with available commands."""
        help_lines = [
            "SafeClaw - Your privacy-first automation assistant",
            "",
            "Available commands:",
        ]

        for intent in self.parser.get_intents():
            examples = self.parser.get_examples(intent)
            if examples:
                help_lines.append(f"  • {intent}: {examples[0]}")

        help_lines.extend([
            "",
            "Available actions:",
        ])

        for action in self.actions:
            help_lines.append(f"  • {action}")

        return "\n".join(help_lines)
