import os
import sqlite3
from typing import Any


class DatabaseManager:
    """
    SQLite Database Manager for AndromedaAI.
    Manages targets, reconnaissance data, and AI micro-step logs.
    """
    def __init__(self, db_path: str = "db/andromeda.db"):
        self.db_path = db_path
        db_dir = os.path.dirname(self.db_path)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir, exist_ok=True)
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        """Creates and returns a sqlite3 connection with Row factory."""
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON;")
        return conn

    def _init_db(self) -> None:
        """Initializes database tables if they do not exist."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Targets table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS targets (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    host TEXT UNIQUE,
                    description TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)

            # Recon Data table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS recon_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    target_id INTEGER,
                    port INTEGER,
                    protocol TEXT,
                    service TEXT,
                    version TEXT,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)

            # AI Logs table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS ai_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    step_name TEXT,
                    raw_input TEXT,
                    ai_output TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            conn.commit()

    def add_target(self, host: str, description: str = "") -> None:
        """Safely inserts a target into targets table using INSERT OR IGNORE."""
        host = host.strip()
        description = description.strip()
        if not host:
            return
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT OR IGNORE INTO targets (host, description) VALUES (?, ?);",
                (host, description)
            )
            conn.commit()

    def get_all_targets(self) -> list[str]:
        """
        Queries targets table and returns a simple list of host strings.
        Returns empty list [] if database is empty.
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT host FROM targets ORDER BY id DESC;")
            rows = cursor.fetchall()
            return [row["host"] for row in rows if row["host"]]

    def delete_target(self, host: str) -> bool:
        """Deletes a target by host string or ID."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM targets WHERE host = ? OR id = ?;", (host, host))
            conn.commit()
            return cursor.rowcount > 0

    def save_ai_log(self, step_name: str, raw_input: str, ai_output: str) -> int:
        """Records an AI micro-step log entry."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO ai_logs (step_name, raw_input, ai_output) VALUES (?, ?, ?);",
                (step_name, raw_input, ai_output)
            )
            conn.commit()
            return cursor.lastrowid

    def get_all_ai_logs(self, limit: int = 50) -> list[dict[str, Any]]:
        """Retrieves recent AI logs for Task History."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, step_name, raw_input, ai_output, timestamp FROM ai_logs ORDER BY id DESC LIMIT ?;",
                (limit,)
            )
            rows = cursor.fetchall()
            return [dict(row) for row in rows]

    def get_ai_log_by_id(self, log_id: int) -> dict[str, Any] | None:
        """Retrieves a specific AI log entry by ID."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, step_name, raw_input, ai_output, timestamp FROM ai_logs WHERE id = ?;",
                (log_id,)
            )
            row = cursor.fetchone()
            return dict(row) if row else None

    def add_recon_service(self, target_host: str, port: int, service: str, version: str = "", protocol: str = "tcp") -> None:
        """Saves parsed service information for bruteforce/exploit mapping."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM targets WHERE host = ?;", (target_host,))
            target_row = cursor.fetchone()
            target_id = target_row["id"] if target_row else None
            
            cursor.execute(
                """
                INSERT INTO recon_data (target_id, port, protocol, service, version)
                VALUES (?, ?, ?, ?, ?);
                """,
                (target_id or 0, port, protocol, service, version)
            )
            conn.commit()

    def get_recon_services(self) -> list[dict[str, Any]]:
        """Retrieves all parsed recon services."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT r.id, t.host, r.port, r.protocol, r.service, r.version, r.updated_at
                FROM recon_data r
                LEFT JOIN targets t ON r.target_id = t.id
                ORDER BY r.id DESC;
            """)
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
