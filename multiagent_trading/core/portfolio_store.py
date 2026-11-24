"""Versioned SQLite persistence for paper-trading portfolio snapshots."""
from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from threading import RLock
from typing import Any

from multiagent_trading.models.portfolio import PortfolioState


class PortfolioStore:
    """Persist and restore complete portfolio snapshots.

    Saves are append-only and each snapshot is committed atomically. This store
    is separate from OrderStore and does not claim cross-store atomicity.
    """

    SCHEMA_VERSION = 1

    def __init__(self, db_path: str = "portfolio.sqlite3") -> None:
        self.db_path = db_path
        self._lock = RLock()
        self._connection = sqlite3.connect(
            db_path, timeout=10, check_same_thread=False, isolation_level=None
        )
        if db_path != ":memory:":
            self._connection.execute("PRAGMA journal_mode=WAL")
            self._connection.execute("PRAGMA synchronous=FULL")
        self._connection.execute("""
            CREATE TABLE IF NOT EXISTS portfolio_snapshots (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                schema_version INTEGER NOT NULL,
                created_at TEXT NOT NULL,
                payload_json TEXT NOT NULL
            )
        """)
        self._connection.execute(
            "CREATE INDEX IF NOT EXISTS idx_portfolio_snapshots_created "
            "ON portfolio_snapshots(created_at, id)"
        )

    @staticmethod
    def _encode(snapshot: dict[str, Any]) -> str:
        try:
            return json.dumps(snapshot, sort_keys=True, separators=(",", ":"), allow_nan=False)
        except (TypeError, ValueError) as error:
            raise ValueError("Snapshot não pode ser serializado como JSON finito.") from error

    def save(self, portfolio: PortfolioState) -> int:
        """Atomically append a snapshot and return its monotonically increasing ID."""
        if not isinstance(portfolio, PortfolioState):
            raise TypeError("portfolio tem de ser uma instância de PortfolioState.")
        payload = self._encode(portfolio.snapshot())
        timestamp = datetime.now(timezone.utc).isoformat()
        with self._lock:
            self._connection.execute("BEGIN IMMEDIATE")
            try:
                cursor = self._connection.execute(
                    "INSERT INTO portfolio_snapshots "
                    "(schema_version, created_at, payload_json) VALUES (?, ?, ?)",
                    (self.SCHEMA_VERSION, timestamp, payload),
                )
                snapshot_id = int(cursor.lastrowid)
                self._connection.execute("COMMIT")
                return snapshot_id
            except Exception:
                self._connection.execute("ROLLBACK")
                raise

    def load_latest(self) -> PortfolioState | None:
        """Restore the newest snapshot; reject unknown schema versions."""
        with self._lock:
            row = self._connection.execute(
                "SELECT schema_version, payload_json FROM portfolio_snapshots "
                "ORDER BY id DESC LIMIT 1"
            ).fetchone()
        if row is None:
            return None
        version, payload = row
        if version != self.SCHEMA_VERSION:
            raise ValueError(f"Versão de snapshot não suportada: {version}.")
        try:
            decoded = json.loads(payload)
        except json.JSONDecodeError as error:
            raise ValueError("Snapshot persistido contém JSON inválido.") from error
        return PortfolioState.from_snapshot(decoded)

    def list_snapshots(self, limit: int = 20) -> list[dict[str, Any]]:
        """Return snapshot metadata without decoding portfolio state."""
        if isinstance(limit, bool) or not isinstance(limit, int) or limit < 1:
            raise ValueError("limit tem de ser um inteiro positivo.")
        with self._lock:
            rows = self._connection.execute(
                "SELECT id, schema_version, created_at FROM portfolio_snapshots "
                "ORDER BY id DESC LIMIT ?",
                (limit,),
            ).fetchall()
        return [
            {"id": row[0], "schema_version": row[1], "created_at": row[2]}
            for row in rows
        ]

    def close(self) -> None:
        """Close the SQLite connection."""
        with self._lock:
            self._connection.close()
