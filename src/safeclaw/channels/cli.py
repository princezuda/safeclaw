"""Command-line interface channel."""

import asyncio
import sys
from typing import TYPE_CHECKING

from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel

from safeclaw.channels.base import BaseChannel

if TYPE_CHECKING:
    from safeclaw.core.engine import SafeClaw


class CLIChannel(BaseChannel):
    """
    Interactive command-line interface.

    Features:
    - Rich text formatting
    - Markdown rendering
    - Command history
    - Async input handling
    """

    name = "cli"

    def __init__(self, engine: "SafeClaw"):
        super().__init__(engine)
        self.console = Console()
        self.running = False
        self.user_id = "cli_user"

    async def start(self) -> None:
        """Start the CLI interface."""
        self.running = True

        # 50-star milestone celebration banner
        self.console.print()
        self.console.print(
            Panel.fit(
                "[bold yellow]          50 STARS          [/bold yellow]\n"
                "[bold white]We hit fifty stars on GitHub![/bold white]\n"
                "\n"
                "[dim]Every huge milestone, we add something new.[/dim]\n"
                "[bold cyan]NEW:[/bold cyan] [white]Blog without a language model[/white]\n"
                "[dim]Write blog news, crawl sites for content,[/dim]\n"
                "[dim]and let SafeClaw generate your titles.[/dim]\n"
                "[dim]Type[/dim] [bold]blog help[/bold] [dim]to get started.[/dim]\n"
                "\n"
                "[dim]Next milestone:[/dim] [bold]100 stars[/bold]",
                border_style="yellow",
                title="[bold yellow] MILESTONE [/bold yellow]",
                subtitle="[dim]safeclaw 0.2.1[/dim]",
            )
        )
        self.console.print()
        self.console.print(
            Panel.fit(
                "[bold green]SafeClaw[/bold green] - Privacy-first automation assistant\n"
                "Type [bold]help[/bold] for commands, [bold]quit[/bold] to exit",
                border_style="green",
            )
        )
        self.console.print()

        while self.running:
            try:
                # Get input
                user_input = await self._async_input("[bold cyan]>[/bold cyan] ")

                if not user_input:
                    continue

                # Handle quit
                if user_input.lower() in ("quit", "exit", "q"):
                    self.console.print("[dim]Goodbye![/dim]")
                    break

                # Process message
                response = await self.handle_message(user_input, self.user_id)

                # Display response
                self._display_response(response)

            except KeyboardInterrupt:
                self.console.print("\n[dim]Interrupted. Type 'quit' to exit.[/dim]")
            except EOFError:
                break

        self.running = False

    async def stop(self) -> None:
        """Stop the CLI interface."""
        self.running = False

    async def send(self, user_id: str, message: str) -> None:
        """Send a message (display to console)."""
        if user_id == self.user_id:
            self._display_response(message)

    async def _async_input(self, prompt: str) -> str:
        """Get input asynchronously."""
        self.console.print(prompt, end="")

        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, sys.stdin.readline)

    def _display_response(self, response: str) -> None:
        """Display response with formatting."""
        self.console.print()

        # Check if response looks like markdown
        if any(marker in response for marker in ["**", "•", "```", "- ", "# "]):
            self.console.print(Markdown(response))
        else:
            self.console.print(response)

        self.console.print()
