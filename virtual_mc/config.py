from __future__ import annotations

from pathlib import Path

CSV_HEADERS = [
    "acctno",
    "name",
    "mnem_code",
    "credit",
    "debit",
    "txn_time",
    "trmlid",
    "refno",
    "external_refno",
    "remarks1",
]

DEFAULT_BRANCH_CODE = "000"
DEFAULT_DB_PATH = Path("Database") / "MasterCardReport.db"
DEFAULT_OUTPUT_DIR = Path("output")

# Keep legacy naming pattern for file compatibility.
REPORT_PREFIX = "aub"
REPORT_BASENAME = "hellomoney_virtual_mastercard"

CREATE_SQL_PATH = Path("VB6 FILE") / "hmvirtualmc sqllite create scripts.txt"
INSERT_SQL_PATH = Path("VB6 FILE") / "hmvirtualmc insert scripts.txt"
