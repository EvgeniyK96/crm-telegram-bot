"""Subscribers and watcher state in SQLite. Tiny tables, so a plain sqlite3 connection is enough."""
import json
import sqlite3


class Storage:
    def __init__(self, path: str):
        self.db = sqlite3.connect(path)
        self.db.executescript("""
            CREATE TABLE IF NOT EXISTS subscribers (chat_id INTEGER PRIMARY KEY);
            CREATE TABLE IF NOT EXISTS state (key TEXT PRIMARY KEY, value TEXT NOT NULL);
        """)

    def subscribe(self, chat_id: int) -> None:
        with self.db:
            self.db.execute("INSERT OR IGNORE INTO subscribers VALUES (?)", (chat_id,))

    def unsubscribe(self, chat_id: int) -> None:
        with self.db:
            self.db.execute("DELETE FROM subscribers WHERE chat_id = ?", (chat_id,))

    def is_subscribed(self, chat_id: int) -> bool:
        return self.db.execute("SELECT 1 FROM subscribers WHERE chat_id = ?", (chat_id,)).fetchone() is not None

    def subscribers(self) -> list[int]:
        return [row[0] for row in self.db.execute("SELECT chat_id FROM subscribers")]

    def get(self, key: str, default=None):
        row = self.db.execute("SELECT value FROM state WHERE key = ?", (key,)).fetchone()
        return json.loads(row[0]) if row else default

    def set(self, key: str, value) -> None:
        with self.db:
            self.db.execute("INSERT OR REPLACE INTO state VALUES (?, ?)", (key, json.dumps(value)))
