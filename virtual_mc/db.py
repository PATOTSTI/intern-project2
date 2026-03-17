from __future__ import annotations

import sqlite3
from datetime import date
from pathlib import Path
from typing import Any


class VirtualMcRepository:
    """SQLite repository for Virtual Mastercard report processing."""

    def __init__(self, db_path: str | Path) -> None:
        self.db_path = Path(db_path)
        self.conn: sqlite3.Connection | None = None

    def connect(self) -> None:
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row

    def close(self) -> None:
        if self.conn is not None:
            self.conn.close()
            self.conn = None

    def bootstrap_from_sql_files(self, create_script_path: str | Path, insert_script_path: str | Path) -> None:
        conn = self._require_connection()
        if self._has_tables():
            self.ensure_support_tables()
            self.ensure_virtual_view()
            return

        self._run_sql_script(Path(create_script_path))
        self._run_sql_script(Path(insert_script_path))
        self.ensure_support_tables()
        self.ensure_virtual_view()
        conn.commit()

    def prepare_report_parameters(self, previous_business_date: date, branch_code: str) -> None:
        conn = self._require_connection()
        month_term = str(previous_business_date.month)
        prev_date = previous_business_date.strftime("%Y-%m-%d")

        for table_name in ("month", "branch_to", "prevbusdate"):
            conn.execute(f"DELETE FROM {table_name}")

        conn.execute("INSERT INTO month(term) VALUES (?)", (month_term,))
        conn.execute("INSERT INTO branch_to(branchno) VALUES (?)", (branch_code,))
        conn.execute("INSERT INTO prevbusdate(date) VALUES (?)", (prev_date,))
        conn.commit()

    def query_report_rows(self) -> list[dict[str, Any]]:
        conn = self._require_connection()
        cursor = conn.execute(
            """
            SELECT acctno, Name, mnem_code, Credit, Debit, txn_time, trmlid, refno,
                   external_refno, remarks1
            FROM vwd_hm_virtual_mc
            ORDER BY txn_date, txn_time
            """
        )
        return [dict(row) for row in cursor.fetchall()]

    def ensure_support_tables(self) -> None:
        conn = self._require_connection()
        conn.execute("CREATE TABLE IF NOT EXISTS month(term TEXT)")
        conn.execute("CREATE TABLE IF NOT EXISTS branch_to(branchno TEXT)")
        conn.execute("CREATE TABLE IF NOT EXISTS prevbusdate(date TEXT)")

    def ensure_virtual_view(self) -> None:
        conn = self._require_connection()
        conn.execute("DROP VIEW IF EXISTS vwd_hm_virtual_mc")
        conn.execute(
            """
            CREATE VIEW vwd_hm_virtual_mc AS
            SELECT
                a.acctno,
                TRIM(COALESCE(c.lname, '')) || ', ' || TRIM(COALESCE(c.fname, '')) || ' ' || TRIM(COALESCE(c.mname, '')) AS Name,
                a.mnem_code,
                CASE WHEN a.txntype = 'D' THEN CAST(a.txnamt AS REAL) ELSE 0 END AS Credit,
                CASE WHEN a.txntype = 'C' THEN CAST(a.txnamt AS REAL) ELSE 0 END AS Debit,
                a.txn_date,
                a.txn_time,
                SUBSTR(a.txncode, 1, 4) AS trmlid,
                a.refno,
                b.external_refno,
                a.remarks1
            FROM hmhistoryfile2_copy AS a
            JOIN cardhistoryfile1_copy AS b
              ON a.refno = b.internal_refno
            JOIN hmacctmstr_copy AS d
              ON a.acctno = d.acctno
            JOIN hmclientmstr_copy AS c
              ON d.clientid = c.clientid
             AND d.partner_id = c.partner_id
            WHERE a.mnem_code IN ('EPOS', 'REPOS')
              AND b.txn_desc = 'OPENLOOP_PRE_AUTH'
            """
        )

    def _run_sql_script(self, script_path: Path) -> None:
        if not script_path.exists():
            raise FileNotFoundError(f"SQL script not found: {script_path}")

        raw_text = script_path.read_text(encoding="utf-8")
        statements = [
            chunk.strip()
            for chunk in raw_text.replace("\r", "").replace("GO", "").split(";")
            if chunk.strip()
        ]

        conn = self._require_connection()
        for statement in statements:
            conn.execute(statement)

    def _has_tables(self) -> bool:
        conn = self._require_connection()
        cursor = conn.execute(
            "SELECT COUNT(*) AS count FROM sqlite_master WHERE type = 'table'"
        )
        return int(cursor.fetchone()["count"]) > 0

    def _require_connection(self) -> sqlite3.Connection:
        if self.conn is None:
            raise RuntimeError("Database connection is not open. Call connect() first.")
        return self.conn
