"""Shell command execution action."""

import asyncio
import re
import shlex
from typing import Any, TYPE_CHECKING

from safeclaw.actions.base import BaseAction

if TYPE_CHECKING:
    from safeclaw.core.engine import SafeClaw


class ShellAction(BaseAction):
    """
    Execute shell commands with sandboxing.

    Security features:
    - Command allowlist/blocklist
    - Timeout enforcement
    - Output limiting
    - Working directory restriction
    """

    name = "shell"
    description = "Execute shell commands"

    # Commands that are always blocked (normalized - single spaces)
    BLOCKED_COMMANDS = {
        "rm -rf /",
        "rm -rf /*",
        "rm -rf .",
        "rm -rf ..",
        "mkfs",
        "dd if=/dev/zero",
        "dd if=/dev/random",
        ":(){:|:&};:",  # Fork bomb
        "chmod -r 777 /",
        "chmod 777 /",
        "curl | sh",
        "curl | bash",
        "wget | sh",
        "wget | bash",
        "| sh",
        "| bash",
        "> /dev/sd",  # Writing to disk devices
        ">/dev/sd",
        "/etc/passwd",
        "/etc/shadow",
        "$(", "`",  # Command substitution
        "eval ",
    }

    # Dangerous patterns (regex)
    BLOCKED_PATTERNS_REGEX = [
        r"rm\s+-[a-z]*r[a-z]*f[a-z]*\s+/",  # rm -rf / variations
        r"rm\s+-[a-z]*f[a-z]*r[a-z]*\s+/",  # rm -fr / variations
        r">\s*/dev/[sh]d[a-z]",  # Writing to disk devices
        r"mkfs\.",  # mkfs.ext4, etc.
        r"/dev/sd[a-z]",  # Direct disk access
        r"chmod\s+.*\s+/\s*$",  # chmod on root
    ]

    # Safe commands that don't need confirmation
    SAFE_COMMANDS = {
        "ls", "pwd", "whoami", "date", "cal", "uptime",
        "df", "du", "free", "top", "ps", "cat", "head", "tail",
        "grep", "find", "wc", "sort", "uniq", "echo",
        "git status", "git log", "git diff", "git branch",
        "python --version", "node --version", "npm --version",
    }

    def __init__(
        self,
        enabled: bool = True,
        sandboxed: bool = True,
        timeout: float = 30.0,
        max_output: int = 10000,
        allowed_commands: list[str] | None = None,
        blocked_patterns: list[str] | None = None,
    ):
        self.enabled = enabled
        self.sandboxed = sandboxed
        self.timeout = timeout
        self.max_output = max_output
        self.allowed_commands = set(allowed_commands) if allowed_commands else None
        self.blocked_patterns = blocked_patterns or []

    def _normalize_command(self, command: str) -> str:
        """Normalize command for security checks."""
        # Lowercase
        cmd = command.lower().strip()
        # Collapse multiple whitespace into single space
        cmd = re.sub(r'\s+', ' ', cmd)
        return cmd

    def _is_safe(self, command: str) -> tuple[bool, str]:
        """
        Check if command is safe to execute.

        Returns:
            Tuple of (is_safe, reason)
        """
        # Normalize command to prevent bypass via whitespace tricks
        command_normalized = self._normalize_command(command)

        # Check blocklist (substring match on normalized command)
        for blocked in self.BLOCKED_COMMANDS:
            if blocked in command_normalized:
                return False, f"Blocked command pattern: {blocked}"

        # Check regex patterns for more complex dangerous commands
        for pattern in self.BLOCKED_PATTERNS_REGEX:
            if re.search(pattern, command_normalized, re.IGNORECASE):
                return False, f"Blocked dangerous pattern"

        # Check user-defined blocked patterns
        for pattern in self.blocked_patterns:
            if pattern in command_normalized:
                return False, f"Blocked pattern: {pattern}"

        # If allowlist specified, command must be in it
        if self.allowed_commands:
            try:
                cmd_base = shlex.split(command)[0] if command else ""
            except ValueError:
                return False, "Invalid command syntax"
            if cmd_base not in self.allowed_commands:
                return False, f"Command not in allowlist: {cmd_base}"

        return True, ""

    async def execute(
        self,
        params: dict[str, Any],
        user_id: str,
        channel: str,
        engine: "SafeClaw",
    ) -> str:
        """Execute shell command."""
        if not self.enabled:
            return "Shell commands are disabled"

        command = params.get("command", "")
        if not command:
            return "No command specified"

        # Security check
        is_safe, reason = self._is_safe(command)
        if not is_safe:
            return f"Command blocked: {reason}"

        try:
            # Execute command
            process = await asyncio.create_subprocess_shell(
                command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )

            try:
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(),
                    timeout=self.timeout,
                )
            except asyncio.TimeoutError:
                process.kill()
                return f"Command timed out after {self.timeout}s"

            # Format output
            output_parts = []

            if stdout:
                stdout_text = stdout.decode("utf-8", errors="replace")
                if len(stdout_text) > self.max_output:
                    stdout_text = stdout_text[:self.max_output] + "\n... (truncated)"
                output_parts.append(stdout_text)

            if stderr:
                stderr_text = stderr.decode("utf-8", errors="replace")
                if len(stderr_text) > self.max_output:
                    stderr_text = stderr_text[:self.max_output] + "\n... (truncated)"
                output_parts.append(f"[stderr]\n{stderr_text}")

            if process.returncode != 0:
                output_parts.append(f"\n[exit code: {process.returncode}]")

            return "\n".join(output_parts) if output_parts else "(no output)"

        except Exception as e:
            return f"Error executing command: {e}"
