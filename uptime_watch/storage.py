"""SQLite-backed storage for check history and uptime calculations."""
from __future__ import annotations

import sqlite3
import time
from dataclasses import dataclass

from uptime_watch.checker import CheckResult

SCHEMA = """
CREATE TABLE IF NOT EXISTS checks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    service_name TEXT NOT NULL,
    url TEXT NOT NULL,
    is_up INTEGER NOT NULL,
    status_code INTEGER,
    response_time_ms REAL,
    error TEXT,
    checked_at REAL NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_checks_service_time
    ON checks (service_name, checked_at);
"""


@dataclass
class UptimeStats:
    service_name: str
    total_checks: int
    up_checks: int
    uptime_percent: float
    avg_response_time_ms: float | None
    last_status: bool | None


class HistoryStore:
    """Thin wrapper around SQLite for storing and querying check results."""

    def __init__(self, db_path: str = ":memory:") -> None:
        self._conn = sqlite3.connect(db_path)
        self._conn.executescript(SCHEMA)
        self._conn.commit()

    def record(self, result: CheckResult) -> None:
        self._conn.execute(
            """INSERT INTO checks
               (service_name, url, is_up, status_code, response_time_ms, error, checked_at)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (
                result.service_name,
                result.url,
                int(result.is_up),
                result.status_code,
                result.response_time_ms,
                result.error,
                result.checked_at,
            ),
        )
        self._conn.commit()

    def record_all(self, results: list[CheckResult]) -> None:
        for result in results:
            self.record(result)

    def uptime_stats(self, service_name: str, since_seconds: float | None = None) -> UptimeStats:
        query = "SELECT is_up, response_time_ms FROM checks WHERE service_name = ?"
        params: list = [service_name]
        if since_seconds is not None:
            query += " AND checked_at >= ?"
            params.append(time.time() - since_seconds)

        rows = self._conn.execute(query, params).fetchall()
        total = len(rows)
        up = sum(1 for is_up, _ in rows if is_up)
        response_times = [rt for _, rt in rows if rt is not None]
        avg_rt = sum(response_times) / len(response_times) if response_times else None

        last_row = self._conn.execute(
            "SELECT is_up FROM checks WHERE service_name = ? ORDER BY checked_at DESC LIMIT 1",
            (service_name,),
        ).fetchone()
        last_status = bool(last_row[0]) if last_row else None

        return UptimeStats(
            service_name=service_name,
            total_checks=total,
            up_checks=up,
            uptime_percent=round((up / total) * 100, 2) if total else 0.0,
            avg_response_time_ms=round(avg_rt, 2) if avg_rt is not None else None,
            last_status=last_status,
        )

    def recent_incidents(self, service_name: str, limit: int = 10) -> list[dict]:
        rows = self._conn.execute(
            """SELECT checked_at, status_code, error FROM checks
               WHERE service_name = ? AND is_up = 0
               ORDER BY checked_at DESC LIMIT ?""",
            (service_name, limit),
        ).fetchall()
        return [{"checked_at": r[0], "status_code": r[1], "error": r[2]} for r in rows]

    def close(self) -> None:
        self._conn.close()
