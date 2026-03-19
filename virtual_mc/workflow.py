from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from pathlib import Path

from .config import (
    CREATE_SQL_PATH,
    DEFAULT_BRANCH_CODE,
    DEFAULT_DB_PATH,
    DEFAULT_OUTPUT_DIR,
    INSERT_SQL_PATH,
    REPORT_BASENAME,
    REPORT_PREFIX,
)
from .date_utils import previous_business_day
from .db import VirtualMcRepository
from .exporters import export_csv, export_excel_like


@dataclass
class ReportResult:
    previous_business_date: date
    row_count: int
    xls_path: Path
    csv_path: Path
    skipped_existing_xls: bool


class VirtualMcReportService:
    """Main workflow service that mirrors legacy business behavior."""

    def __init__(
        self,
        db_path: Path = DEFAULT_DB_PATH,
        output_dir: Path = DEFAULT_OUTPUT_DIR,
        branch_code: str = DEFAULT_BRANCH_CODE,
    ) -> None:
        self.db_path = db_path
        self.output_dir = output_dir
        self.branch_code = branch_code

    def run(self, report_date: date | None = None) -> ReportResult:
        previous_date = previous_business_day(report_date)
        yyyymmdd = previous_date.strftime("%Y%m%d")

        base_name = f"{REPORT_PREFIX}{self.branch_code}{REPORT_BASENAME}_{yyyymmdd}"
        xls_path = self.output_dir / f"{base_name}.xls"
        csv_path = self.output_dir / f"{base_name}.csv"

        if xls_path.exists():
            return ReportResult(
                previous_business_date=previous_date,
                row_count=0,
                xls_path=xls_path,
                csv_path=csv_path,
                skipped_existing_xls=True,
            )

        repo = VirtualMcRepository(self.db_path)
        repo.connect()
        try:
            repo.bootstrap_from_sql_files(CREATE_SQL_PATH, INSERT_SQL_PATH)
            repo.prepare_report_parameters(previous_date, self.branch_code)
            rows = repo.query_report_rows(previous_date)

            export_excel_like(xls_path, rows, previous_date)
            export_csv(csv_path, rows)

            return ReportResult(
                previous_business_date=previous_date,
                row_count=len(rows),
                xls_path=xls_path,
                csv_path=csv_path,
                skipped_existing_xls=False,
            )
        finally:
            repo.close()
