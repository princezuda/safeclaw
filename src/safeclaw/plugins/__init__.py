"""
SafeClaw Plugin System.

Plugins extend SafeClaw with new actions and intents.

Directory structure:
- plugins/official/  - Curated, tested plugins
- plugins/community/ - User-contributed plugins

To create a plugin, see plugins/base.py for documentation.
"""

from safeclaw.plugins.base import BasePlugin, PluginInfo
from safeclaw.plugins.loader import PluginLoader

__all__ = ["BasePlugin", "PluginInfo", "PluginLoader"]
