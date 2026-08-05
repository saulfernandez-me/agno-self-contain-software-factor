import sqlite3
import time
from pathlib import Path

SCHEMA = """
CREATE TABLE IF NOT EXISTS sessions (
    id TEXT PRIMARY KEY,
    name TEXT,
    started_at REAL,
    ended_at REAL,
    status TEXT
);
CREATE TABLE IF NOT EXISTS phases (
    id TEXT PRIMARY KEY,
    session_id TEXT,
    lane TEXT,
    started_at REAL,
    ended_at REAL,
    duration_ms REAL
);
"""


class TelemetryDB:
    """
    SQLite WAL-mode tracer for ASSF workflows.
    Records sessions, phases, and execution metrics without blocking.
    """

    def __init__(self, db_path: str = ".context/data/telemetry.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        # check_same_thread=False allows sharing across contexts if necessary
        self.conn = sqlite3.connect(str(self.db_path), check_same_thread=False)
        self.conn.execute("PRAGMA journal_mode=WAL;")
        self.conn.executescript(SCHEMA)
        self.conn.commit()

    def start_session(self, session_id: str, name: str) -> None:
        self.conn.execute(
            "INSERT OR REPLACE INTO sessions (id, name, started_at, status) VALUES (?, ?, ?, ?)",
            (session_id, name, time.time(), "running"),
        )
        self.conn.commit()

    def end_session(self, session_id: str, status: str) -> None:
        self.conn.execute(
            "UPDATE sessions SET ended_at = ?, status = ? WHERE id = ?",
            (time.time(), status, session_id),
        )
        self.conn.commit()

    def log_phase(
        self,
        phase_id: str,
        session_id: str,
        lane: str,
        started_at: float,
        ended_at: float,
    ) -> None:
        duration = (ended_at - started_at) * 1000
        self.conn.execute(
            "INSERT INTO phases (id, session_id, lane, started_at, ended_at, duration_ms) VALUES (?, ?, ?, ?, ?, ?)",
            (phase_id, session_id, lane, started_at, ended_at, duration),
        )
        self.conn.commit()
