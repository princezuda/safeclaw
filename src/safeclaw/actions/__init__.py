"""SafeClaw actions - things the assistant can do."""

from safeclaw.actions.blog import BlogAction
from safeclaw.actions.briefing import BriefingAction
from safeclaw.actions.calendar import CalendarAction
from safeclaw.actions.crawl import CrawlAction
from safeclaw.actions.email import EmailAction
from safeclaw.actions.files import FilesAction
from safeclaw.actions.news import NewsAction
from safeclaw.actions.reminder import ReminderAction
from safeclaw.actions.shell import ShellAction
from safeclaw.actions.summarize import SummarizeAction

__all__ = [
    "BlogAction",
    "FilesAction",
    "ShellAction",
    "SummarizeAction",
    "CrawlAction",
    "ReminderAction",
    "BriefingAction",
    "NewsAction",
    "EmailAction",
    "CalendarAction",
]
