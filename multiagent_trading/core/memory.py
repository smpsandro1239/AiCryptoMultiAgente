import sqlite3
import json
from datetime import datetime
from typing import Any, List

class PersistentSemanticMemory:
    def __init__(self, db_path="memory.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS memory (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT,
                    key TEXT,
                    value TEXT
                )
            """)

    def add(self, key: str, value: Any):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT INTO memory (timestamp, key, value) VALUES (?, ?, ?)",
                (datetime.now().isoformat(), key, json.dumps(value))
            )

    def query(self, query_str: str) -> List[dict]:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "SELECT timestamp, key, value FROM memory WHERE value LIKE ?",
                (f"%{query_str}%",)
            )
            return [
                {"timestamp": row[0], "key": row[1], "value": json.loads(row[2])}
                for row in cursor.fetchall()
            ]
