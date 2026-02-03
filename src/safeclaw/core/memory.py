"""
SafeClaw Memory - Persistent storage for conversations and data.

SQLite-based with async support. No cloud required.
"""

import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Optional

import aiosqlite

logger = logging.getLogger(__name__)


class Memory:
    """
    Persistent memory storage using SQLite.

    Stores:
    - Conversation history
    - User preferences
    - Scheduled tasks
    - Webhook configurations
    - Crawl cache
    """

    def __init__(self, db_path: Path):
        self.db_path = db_path
        self._connection: Optional[aiosqlite.Connection] = None

    async def initialize(self) -> None:
        """Initialize database and create tables."""
        self._connection = await aiosqlite.connect(self.db_path)
        await self._create_tables()
        logger.info(f"Memory initialized at {self.db_path}")

    async def _create_tables(self) -> None:
        """Create database tables if they don't exist."""
        assert self._connection is not None

        await self._connection.executescript("""
            -- Conversation history
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                channel TEXT NOT NULL,
                text TEXT NOT NULL,
                intent TEXT,
                params TEXT,
                metadata TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            CREATE INDEX IF NOT EXISTS idx_messages_user ON messages(user_id);
            CREATE INDEX IF NOT EXISTS idx_messages_channel ON messages(channel);
            CREATE INDEX IF NOT EXISTS idx_messages_created ON messages(created_at);

            -- User preferences and settings
            CREATE TABLE IF NOT EXISTS preferences (
                user_id TEXT PRIMARY KEY,
                data TEXT NOT NULL,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            -- Scheduled reminders and tasks
            CREATE TABLE IF NOT EXISTS reminders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                channel TEXT NOT NULL,
                task TEXT NOT NULL,
                trigger_at TIMESTAMP NOT NULL,
                repeat TEXT,
                completed INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            CREATE INDEX IF NOT EXISTS idx_reminders_trigger ON reminders(trigger_at);
            CREATE INDEX IF NOT EXISTS idx_reminders_user ON reminders(user_id);

            -- Webhook configurations
            CREATE TABLE IF NOT EXISTS webhooks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                secret TEXT,
                action TEXT NOT NULL,
                params TEXT,
                enabled INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            -- Crawl cache
            CREATE TABLE IF NOT EXISTS crawl_cache (
                url TEXT PRIMARY KEY,
                content TEXT,
                links TEXT,
                summary TEXT,
                fetched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP
            );
            CREATE INDEX IF NOT EXISTS idx_crawl_expires ON crawl_cache(expires_at);

            -- Key-value store for arbitrary data
            CREATE TABLE IF NOT EXISTS keyvalue (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL,
                expires_at TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        await self._connection.commit()

    async def close(self) -> None:
        """Close database connection."""
        if self._connection:
            await self._connection.close()
            self._connection = None
            logger.info("Memory connection closed")

    # Message storage
    async def store_message(
        self,
        user_id: str,
        channel: str,
        text: str,
        parsed: Any,
        metadata: Optional[dict] = None,
    ) -> int:
        """Store a message in history."""
        assert self._connection is not None

        cursor = await self._connection.execute(
            """
            INSERT INTO messages (user_id, channel, text, intent, params, metadata)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                user_id,
                channel,
                text,
                parsed.intent if parsed else None,
                json.dumps(parsed.params) if parsed else None,
                json.dumps(metadata) if metadata else None,
            ),
        )
        await self._connection.commit()
        return cursor.lastrowid or 0

    async def get_history(
        self,
        user_id: str,
        limit: int = 50,
        channel: Optional[str] = None,
    ) -> list[dict[str, Any]]:
        """Retrieve conversation history for a user."""
        assert self._connection is not None

        query = "SELECT * FROM messages WHERE user_id = ?"
        params: list[Any] = [user_id]

        if channel:
            query += " AND channel = ?"
            params.append(channel)

        query += " ORDER BY created_at DESC LIMIT ?"
        params.append(limit)

        cursor = await self._connection.execute(query, params)
        rows = await cursor.fetchall()

        return [
            {
                "id": row[0],
                "user_id": row[1],
                "channel": row[2],
                "text": row[3],
                "intent": row[4],
                "params": json.loads(row[5]) if row[5] else None,
                "metadata": json.loads(row[6]) if row[6] else None,
                "created_at": row[7],
            }
            for row in reversed(rows)
        ]

    # Preferences
    async def set_preference(self, user_id: str, key: str, value: Any) -> None:
        """Set a user preference."""
        assert self._connection is not None

        # Get existing preferences
        cursor = await self._connection.execute(
            "SELECT data FROM preferences WHERE user_id = ?", (user_id,)
        )
        row = await cursor.fetchone()

        if row:
            prefs = json.loads(row[0])
        else:
            prefs = {}

        prefs[key] = value

        await self._connection.execute(
            """
            INSERT OR REPLACE INTO preferences (user_id, data, updated_at)
            VALUES (?, ?, CURRENT_TIMESTAMP)
            """,
            (user_id, json.dumps(prefs)),
        )
        await self._connection.commit()

    async def get_preference(self, user_id: str, key: str, default: Any = None) -> Any:
        """Get a user preference."""
        assert self._connection is not None

        cursor = await self._connection.execute(
            "SELECT data FROM preferences WHERE user_id = ?", (user_id,)
        )
        row = await cursor.fetchone()

        if row:
            prefs = json.loads(row[0])
            return prefs.get(key, default)

        return default

    # Reminders
    async def add_reminder(
        self,
        user_id: str,
        channel: str,
        task: str,
        trigger_at: datetime,
        repeat: Optional[str] = None,
    ) -> int:
        """Add a reminder."""
        assert self._connection is not None

        cursor = await self._connection.execute(
            """
            INSERT INTO reminders (user_id, channel, task, trigger_at, repeat)
            VALUES (?, ?, ?, ?, ?)
            """,
            (user_id, channel, task, trigger_at.isoformat(), repeat),
        )
        await self._connection.commit()
        return cursor.lastrowid or 0

    async def get_pending_reminders(self, before: Optional[datetime] = None) -> list[dict]:
        """Get reminders that are due."""
        assert self._connection is not None

        before = before or datetime.now()

        cursor = await self._connection.execute(
            """
            SELECT * FROM reminders
            WHERE completed = 0 AND trigger_at <= ?
            ORDER BY trigger_at
            """,
            (before.isoformat(),),
        )
        rows = await cursor.fetchall()

        return [
            {
                "id": row[0],
                "user_id": row[1],
                "channel": row[2],
                "task": row[3],
                "trigger_at": datetime.fromisoformat(row[4]),
                "repeat": row[5],
                "completed": bool(row[6]),
                "created_at": row[7],
            }
            for row in rows
        ]

    async def complete_reminder(self, reminder_id: int) -> None:
        """Mark a reminder as completed."""
        assert self._connection is not None

        await self._connection.execute(
            "UPDATE reminders SET completed = 1 WHERE id = ?",
            (reminder_id,),
        )
        await self._connection.commit()

    # Webhooks
    async def add_webhook(
        self,
        name: str,
        action: str,
        params: Optional[dict] = None,
        secret: Optional[str] = None,
    ) -> None:
        """Register a webhook."""
        assert self._connection is not None

        await self._connection.execute(
            """
            INSERT OR REPLACE INTO webhooks (name, secret, action, params)
            VALUES (?, ?, ?, ?)
            """,
            (name, secret, action, json.dumps(params) if params else None),
        )
        await self._connection.commit()

    async def get_webhook(self, name: str) -> Optional[dict]:
        """Get a webhook by name."""
        assert self._connection is not None

        cursor = await self._connection.execute(
            "SELECT * FROM webhooks WHERE name = ? AND enabled = 1",
            (name,),
        )
        row = await cursor.fetchone()

        if row:
            return {
                "id": row[0],
                "name": row[1],
                "secret": row[2],
                "action": row[3],
                "params": json.loads(row[4]) if row[4] else None,
                "enabled": bool(row[5]),
                "created_at": row[6],
            }

        return None

    async def list_webhooks(self) -> list[dict]:
        """List all webhooks."""
        assert self._connection is not None

        cursor = await self._connection.execute("SELECT * FROM webhooks")
        rows = await cursor.fetchall()

        return [
            {
                "id": row[0],
                "name": row[1],
                "secret": row[2],
                "action": row[3],
                "params": json.loads(row[4]) if row[4] else None,
                "enabled": bool(row[5]),
                "created_at": row[6],
            }
            for row in rows
        ]

    # Crawl cache
    async def cache_crawl(
        self,
        url: str,
        content: str,
        links: list[str],
        summary: Optional[str] = None,
        ttl_hours: int = 24,
    ) -> None:
        """Cache crawl results."""
        assert self._connection is not None

        expires_at = datetime.now() + timedelta(hours=ttl_hours)

        await self._connection.execute(
            """
            INSERT OR REPLACE INTO crawl_cache (url, content, links, summary, fetched_at, expires_at)
            VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP, ?)
            """,
            (url, content, json.dumps(links), summary, expires_at.isoformat()),
        )
        await self._connection.commit()

    async def get_cached_crawl(self, url: str) -> Optional[dict]:
        """Get cached crawl result if not expired."""
        assert self._connection is not None

        cursor = await self._connection.execute(
            """
            SELECT * FROM crawl_cache
            WHERE url = ? AND expires_at > CURRENT_TIMESTAMP
            """,
            (url,),
        )
        row = await cursor.fetchone()

        if row:
            return {
                "url": row[0],
                "content": row[1],
                "links": json.loads(row[2]) if row[2] else [],
                "summary": row[3],
                "fetched_at": row[4],
                "expires_at": row[5],
            }

        return None

    # Key-value store
    async def set(self, key: str, value: Any, ttl_seconds: Optional[int] = None) -> None:
        """Set a key-value pair."""
        assert self._connection is not None

        expires_at = None
        if ttl_seconds:
            expires_at = (datetime.now() + timedelta(seconds=ttl_seconds)).isoformat()

        await self._connection.execute(
            """
            INSERT OR REPLACE INTO keyvalue (key, value, expires_at, updated_at)
            VALUES (?, ?, ?, CURRENT_TIMESTAMP)
            """,
            (key, json.dumps(value), expires_at),
        )
        await self._connection.commit()

    async def get(self, key: str, default: Any = None) -> Any:
        """Get a value by key."""
        assert self._connection is not None

        cursor = await self._connection.execute(
            """
            SELECT value FROM keyvalue
            WHERE key = ? AND (expires_at IS NULL OR expires_at > CURRENT_TIMESTAMP)
            """,
            (key,),
        )
        row = await cursor.fetchone()

        if row:
            return json.loads(row[0])

        return default
