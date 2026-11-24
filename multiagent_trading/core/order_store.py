"""SQLite-backed order idempotency ledger for paper execution."""
from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from threading import RLock
from typing import Any


class OrderStore:
    """Persist order claims and terminal states with a unique order identifier.

    A stale pending row is intentionally retained after an interrupted process.
    It prevents an uncertain order from being replayed automatically (fail closed).
    """

    _VALID_STATUSES = {"pending", "filled", "rejected"}

    def __init__(self, db_path: str = ":memory:") -> None:
        self.db_path = db_path
        self._lock = RLock()
        self._connection = sqlite3.connect(
            db_path,
            timeout=10,
            check_same_thread=False,
        )
        if db_path != ":memory:":
            self._connection.execute("PRAGMA journal_mode=WAL")
            self._connection.execute("PRAGMA synchronous=FULL")
        self._connection.execute(
            """
            CREATE TABLE IF NOT EXISTS orders (
                order_id TEXT PRIMARY KEY,
                status TEXT NOT NULL CHECK(status IN ('pending', 'filled', 'rejected')),
                payload_json TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )
        self._connection.commit()

    @staticmethod
    def _now() -> str:
        return datetime.now(timezone.utc).isoformat()

    def reserve(self, order_id: str, payload: dict[str, Any]) -> bool:
        """Atomically reserve an order ID; return False if it already exists."""
        if not isinstance(order_id, str) or not order_id.strip():
            raise ValueError("order_id é obrigatório.")
        encoded = json.dumps(payload, sort_keys=True, default=str, allow_nan=False)
        now = self._now()
        with self._lock:
            cursor = self._connection.execute(
                """
                INSERT OR IGNORE INTO orders
                    (order_id, status, payload_json, created_at, updated_at)
                VALUES (?, 'pending', ?, ?, ?)
                """,
                (order_id, encoded, now, now),
            )
            self._connection.commit()
            return cursor.rowcount == 1

    def set_status(
        self,
        order_id: str,
        status: str,
        payload: dict[str, Any] | None = None,
    ) -> bool:
        """Transition a pending order to filled/rejected exactly once."""
        if status not in self._VALID_STATUSES - {"pending"}:
            raise ValueError("Estado final de ordem inválido.")
        encoded = json.dumps(payload or {}, sort_keys=True, default=str, allow_nan=False)
        with self._lock:
            cursor = self._connection.execute(
                """
                UPDATE orders
                SET status = ?, payload_json = ?, updated_at = ?
                WHERE order_id = ? AND status = 'pending'
                """,
                (status, encoded, self._now(), order_id),
            )
            self._connection.commit()
            return cursor.rowcount == 1

    def get(self, order_id: str) -> dict[str, Any] | None:
        """Return the persisted order record, or None when it does not exist."""
        with self._lock:
            row = self._connection.execute(
                """
                SELECT order_id, status, payload_json, created_at, updated_at
                FROM orders WHERE order_id = ?
                """,
                (order_id,),
            ).fetchone()
        if row is None:
            return None
        return {
            "order_id": row[0],
            "status": row[1],
            "payload": json.loads(row[2]),
            "created_at": row[3],
            "updated_at": row[4],
        }

    def close(self) -> None:
        """Close the underlying SQLite connection."""
        with self._lock:
            self._connection.close()
