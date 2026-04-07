from __future__ import annotations

from datetime import date, datetime


def parse_report_date(value: str | None) -> date | None:
    if value is None:
        return None
    return datetime.strptime(value, "%Y-%m-%d").date()


