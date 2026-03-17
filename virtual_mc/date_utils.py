from __future__ import annotations

from datetime import date, datetime, timedelta


def parse_report_date(value: str | None) -> date | None:
    if value is None:
        return None
    return datetime.strptime(value, "%Y-%m-%d").date()


def previous_business_day(reference_date: date | None) -> date:
    """Return the previous business day, skipping weekends."""
    base = reference_date or date.today()
    candidate = base - timedelta(days=1)
    while candidate.weekday() >= 5:
        candidate -= timedelta(days=1)
    return candidate
