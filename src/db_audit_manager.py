"""
Module: db_audit_manager.py
Description: Secured transactional persistence and audit logging layer for financial operations.
             Configured with SQLite WAL mode and parameterized queries.
Author: João Pedro Campello
License: MIT
"""

from contextlib import contextmanager
from datetime import datetime
import logging
from pathlib import Path
import sqlite3
from typing import Any, Dict, List, Optional

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")


class DatabaseAuditManager:
    """Manages transactional audit trail database with connection safety."""

    def __init__(self, db_path: Path = Path("data/audit_ledger.db")):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_schema()

    @contextmanager
    def _get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        # Enable Write-Ahead Logging for concurrent read/write throughput
        conn.execute("PRAGMA journal_mode=WAL;")
        try:
            yield conn
            conn.commit()
        except Exception as error:
            conn.rollback()
            logging.error("Transaction rolled back due to error: %s", error)
            raise
        finally:
            conn.close()

    def _init_schema(self) -> None:
        """Creates normalized audit tables if they do not exist."""
        with self._get_connection() as conn:
            conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS operational_refunds (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    reference_code TEXT UNIQUE NOT NULL,
                    account_holder TEXT NOT NULL,
                    amount REAL NOT NULL,
                    reason TEXT NOT NULL,
                    reconciliation_status TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS audit_logs (
                    log_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    event_type TEXT NOT NULL,
                    target_reference TEXT NOT NULL,
                    payload_summary TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                """
            )
            logging.info("Audit schema verified.")

    def record_refund_transaction(
        self, ref_code: str, holder: str, amount: float, reason: str
    ) -> None:
        """Persists a new refund record using parameterized query."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO operational_refunds 
                (reference_code, account_holder, amount, reason, reconciliation_status)
                VALUES (?, ?, ?, ?, 'PROCESSED')
                ON CONFLICT(reference_code) DO UPDATE SET
                reconciliation_status = 'RE-AUDITED';
                """,
                (ref_code, holder, amount, reason),
            )
            cursor.execute(
                """
                INSERT INTO audit_logs (event_type, target_reference, payload_summary)
                VALUES ('REFUND_AUDIT', ?, ?);
                """,
                (ref_code, f"Holder: {holder} | Amount: ${amount:.2f}"),
            )
        logging.info("Transaction %s persisted to secure audit trail.", ref_code)

    def query_by_reference(self, ref_code: str) -> Optional[Dict[str, Any]]:
        """Performs indexed lookup for audit reconciliation."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM operational_refunds WHERE reference_code = ? LIMIT 1;", (ref_code,)
            )
            row = cursor.fetchone()
            return dict(row) if row else None


if __name__ == "__main__":
    db = DatabaseAuditManager(Path("data/mock_audit_ledger.db"))
    db.record_refund_transaction(
        ref_code="REC-80491-X",
        holder="Standard Account Holder",
        amount=540.00,
        reason="Duplicate Payment Adjustment",
    )
    result = db.query_by_reference("REC-80491-X")
    print("\n--- Queried Transaction ---")
    print(result)
