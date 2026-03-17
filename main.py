from __future__ import annotations

import argparse
from pathlib import Path

from virtual_mc.config import DEFAULT_BRANCH_CODE, DEFAULT_DB_PATH, DEFAULT_OUTPUT_DIR
from virtual_mc.date_utils import parse_report_date
from virtual_mc.workflow import VirtualMcReportService


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Generate Virtual Mastercard report outputs.")
    parser.add_argument("--report-date", help="Reference date in YYYY-MM-DD format")
    parser.add_argument("--branch", default=DEFAULT_BRANCH_CODE, help="Branch code (default: 000)")
    parser.add_argument(
        "--db-path",
        default=str(DEFAULT_DB_PATH),
        help="SQLite database path (default: Database/MasterCardReport.db)",
    )
    parser.add_argument(
        "--output-dir",
        default=str(DEFAULT_OUTPUT_DIR),
        help="Output directory for CSV/XLS files",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()

    service = VirtualMcReportService(
        db_path=Path(args.db_path),
        output_dir=Path(args.output_dir),
        branch_code=args.branch,
    )
    result = service.run(report_date=parse_report_date(args.report_date))

    if result.skipped_existing_xls:
        print(f"Skipped: existing XLS already present at {result.xls_path}")
        return 0

    print(f"Previous business date: {result.previous_business_date}")
    print(f"Rows exported: {result.row_count}")
    print(f"XLS: {result.xls_path}")
    print(f"CSV: {result.csv_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
