import sqlite3
import time
from pathlib import Path

from asf_core.telemetry import TelemetryDB


def test_telemetry_db_creation(tmp_path: Path) -> None:
    db_path = tmp_path / "telemetry.db"
    TelemetryDB(str(db_path))

    assert db_path.exists()

    # Check tables
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [row[0] for row in cursor.fetchall()]
    assert "sessions" in tables
    assert "phases" in tables


def test_telemetry_logging(tmp_path: Path) -> None:
    db_path = tmp_path / "telemetry.db"
    db = TelemetryDB(str(db_path))

    db.start_session("ses_123", "test_workflow")
    db.log_phase("phase_abc", "ses_123", "agent", time.time() - 1, time.time())
    db.end_session("ses_123", "completed")

    conn = sqlite3.connect(str(db_path))

    ses = conn.execute("SELECT status FROM sessions WHERE id='ses_123'").fetchone()
    assert ses[0] == "completed"

    phase = conn.execute(
        "SELECT lane, duration_ms FROM phases WHERE id='phase_abc'"
    ).fetchone()
    assert phase[0] == "agent"
    assert phase[1] > 0
