"""CLI entry point for tldr-feed."""

from __future__ import annotations

import sys

import typer
from rich.console import Console
from rich.panel import Panel

from tldr_feed.summarizer import fetch_text, summarize, tldr

app = typer.Typer(
    name="tldr-feed",
    help="Paste a URL, get a summary. No AI, just math.",
    add_completion=False,
)
console = Console()


@app.command()
def main(
    url: str = typer.Argument(..., help="URL to summarize"),
    sentences: int = typer.Option(3, "--sentences", "-n", help="Number of summary sentences"),
    raw: bool = typer.Option(False, "--raw", "-r", help="Print plain text (no formatting)"),
) -> None:
    """Summarize any web page in seconds. No LLM. No API key."""
    try:
        text = fetch_text(url)
    except Exception as exc:
        console.print(f"[red]Error fetching URL:[/red] {exc}", style="bold")
        raise typer.Exit(1)

    if not text:
        console.print("[yellow]No readable text found on that page.[/yellow]")
        raise typer.Exit(1)

    summary = summarize(text, sentences=sentences)

    if raw:
        print(summary)
    else:
        console.print()
        console.print(Panel(summary, title="[bold green]TL;DR[/bold green]", border_style="green"))
        console.print()


def run() -> None:
    app()


if __name__ == "__main__":
    run()
