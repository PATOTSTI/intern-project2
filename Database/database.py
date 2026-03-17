from __future__ import annotations

from datetime import date
from pathlib import Path
from typing import Iterable

from virtual_mc.db import VirtualMcRepository
from virtual_mc.exporters import export_csv, export_excel_like


class DatabaseManager(VirtualMcRepository):
    """Backward-compatible adapter for legacy imports in this project."""

    def connect(self):
        super().connect()
        return self.conn

    def query_virtual_mc_rows(self) -> list[dict[str, object]]:
        return super().query_report_rows()

    def export_excel_like(
        self,
        output_path: str | Path,
        rows: Iterable[dict[str, object]],
        report_date: date | None = None,
    ) -> None:
        export_excel_like(Path(output_path), rows, report_date or date.today())

    def export_csv(self, output_path: str | Path, rows: Iterable[dict[str, object]]) -> None:
        export_csv(Path(output_path), rows)

    def prepare_report_parameters(self, previous_business_date: date, branch_code: str) -> None:
        super().prepare_report_parameters(previous_business_date, branch_code)

    def clear_table(self, table_name: str) -> None:
        conn = self._require_connection()
        conn.execute(f"DELETE FROM {table_name}")


__all__ = ["DatabaseManager"]
