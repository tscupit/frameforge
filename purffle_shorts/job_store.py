"""Durable Studio job snapshots, separate from the video history database.

Jobs interrupted by a process restart are marked failed, not automatically
replayed: an upload or external AI request may have completed before the crash.
"""
from __future__ import annotations

import json
import sqlite3
import threading
import time
from pathlib import Path


class JobStore:
    """SQLite-backed job snapshots with stable, monotonically increasing IDs."""

    def __init__(self, path: str | Path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.Lock()
        with self._connect() as db:
            db.execute("""CREATE TABLE IF NOT EXISTS studio_jobs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                kind TEXT NOT NULL,
                params TEXT NOT NULL,
                label TEXT NOT NULL,
                status TEXT NOT NULL,
                stage TEXT NOT NULL,
                pct INTEGER NOT NULL,
                message TEXT NOT NULL,
                log TEXT NOT NULL,
                result TEXT NOT NULL,
                created REAL NOT NULL,
                started REAL,
                finished REAL
            )""")
            db.execute("CREATE INDEX IF NOT EXISTS studio_jobs_status ON studio_jobs(status)")

    def _connect(self):
        db = sqlite3.connect(self.path, timeout=30)
        db.row_factory = sqlite3.Row
        return db

    def create(self, kind: str, params: dict, label: str) -> dict:
        created = time.time()
        with self._lock, self._connect() as db:
            cur = db.execute(
                """INSERT INTO studio_jobs
                   (kind, params, label, status, stage, pct, message, log, result, created)
                   VALUES (?, ?, ?, 'queued', '', 0, '', '[]', '{}', ?)""",
                (kind, json.dumps(params), label, created),
            )
            return {"id": cur.lastrowid, "created": created}

    def save(self, job) -> None:
        with self._lock, self._connect() as db:
            db.execute(
                """UPDATE studio_jobs SET status=?, stage=?, pct=?, message=?, log=?,
                   result=?, started=?, finished=? WHERE id=?""",
                (job.status, job.stage, job.pct, job.message,
                 json.dumps(job.log[-400:]), json.dumps(job.result),
                 job.started, job.finished, job.id),
            )

    def recover(self) -> None:
        """Never blindly replay interrupted work with external side effects."""
        now = time.time()
        with self._lock, self._connect() as db:
            db.execute(
                """UPDATE studio_jobs SET status='failed', finished=?,
                   message='Interrupted by Studio restart; review before retrying'
                   WHERE status IN ('queued', 'running')""",
                (now,),
            )

    def recent(self, limit: int = 100) -> list[dict]:
        with self._lock, self._connect() as db:
            rows = db.execute(
                "SELECT * FROM studio_jobs ORDER BY id DESC LIMIT ?", (limit,)
            ).fetchall()
        return [
            {**dict(row),
             "params": json.loads(row["params"]),
             "log": json.loads(row["log"]),
             "result": json.loads(row["result"])}
            for row in rows
        ]
