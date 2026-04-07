from __future__ import annotations

import argparse
from datetime import datetime
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
        help="SQLite database path (default: Database/TestDB.db)",
    )
    parser.add_argument(
        "--output-dir",
        default=str(DEFAULT_OUTPUT_DIR),
        help="Output directory for CSV/XLS files",
    )
    return parser


def prompt_report_date() -> str:
    """Interactively ask the user to enter a reference date."""
    print("=" * 50)
    print("  HelloMoney Virtual Mastercard Report")
    print("=" * 50)
    while True:
        raw = input("Enter the report date (YYYY-MM-DD): ").strip()
        try:
            datetime.strptime(raw, "%Y-%m-%d")
            return raw
        except ValueError:
            print(f"  Invalid date '{raw}'. Please use YYYY-MM-DD format (e.g. 2026-03-13).")


def main() -> int:
    args = build_parser().parse_args()

    raw_date = args.report_date or prompt_report_date()

    service = VirtualMcReportService(
        db_path=Path(args.db_path),
        output_dir=Path(args.output_dir),
        branch_code=args.branch,
    )
    result = service.run(report_date=parse_report_date(raw_date))

    if result.skipped_existing_xls:
        print(f"Skipped: existing XLS already present at {result.xls_path}")
        return 0

    print(f"\nReport date : {result.report_date}")
    print(f"Rows exported: {result.row_count}")
    print(f"XLS : {result.xls_path}")
    print(f"CSV : {result.csv_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
