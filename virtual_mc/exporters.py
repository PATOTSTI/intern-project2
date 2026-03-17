from __future__ import annotations

import csv
from datetime import date
from pathlib import Path
from typing import Any, Iterable

import xlwt

from .config import CSV_HEADERS


def export_excel_like(output_path: Path, rows: Iterable[dict[str, Any]], report_date: date) -> None:
    """Generate a real .xls workbook with VB-style layout and summaries."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    row_list = [_map_row(row, sanitize_name=False) for row in rows]
    summary = compute_summaries(row_list)

    workbook = xlwt.Workbook()
    sheet = workbook.add_sheet("Virtual MC")

    title_style = xlwt.easyxf("font: bold on, height 320;")
    subtitle_style = xlwt.easyxf("font: italic on;")
    header_style = xlwt.easyxf("font: bold on; pattern: pattern solid, fore_colour gray25;")
    money_style = xlwt.easyxf(num_format_str="#,##0.00")
    bold_style = xlwt.easyxf("font: bold on;")
    bold_money_style = xlwt.easyxf("font: bold on;", num_format_str="#,##0.00")

    subtitle = f"for {report_date.strftime('%B')} {report_date.day}, {report_date.year}"
    sheet.write(0, 0, "HelloMoney Virtual Mastercard Report", title_style)
    sheet.write(1, 0, subtitle, subtitle_style)

    header_row = 3
    for col_idx, header in enumerate(CSV_HEADERS):
        sheet.write(header_row, col_idx, header, header_style)

    for row_idx, row in enumerate(row_list, start=header_row + 1):
        for col_idx, value in enumerate(row):
            if col_idx in (3, 4):
                sheet.write(row_idx, col_idx, _to_float(value), money_style)
            else:
                sheet.write(row_idx, col_idx, value)

    summary_row = header_row + 1 + len(row_list) + 1
    sheet.write(summary_row, 0, "Total Credit", bold_style)
    sheet.write(summary_row, 1, summary["credit_count"], bold_style)
    sheet.write(summary_row, 2, summary["credit_sum"], bold_money_style)

    sheet.write(summary_row + 1, 0, "Total Debit", bold_style)
    sheet.write(summary_row + 1, 1, summary["debit_count"], bold_style)
    sheet.write(summary_row + 1, 2, summary["debit_sum"], bold_money_style)

    sheet.write(summary_row + 2, 0, "Total App Txn", bold_style)
    sheet.write(summary_row + 2, 1, summary["txn_count"], bold_style)
    sheet.write(summary_row + 2, 2, summary["net_amount"], bold_money_style)

    width_map = [22, 30, 14, 14, 14, 14, 12, 24, 30, 20]
    for idx, width in enumerate(width_map):
        sheet.col(idx).width = width * 256

    workbook.save(str(output_path))


def export_csv(output_path: Path, rows: Iterable[dict[str, Any]]) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(CSV_HEADERS)
        for row in rows:
            writer.writerow(_map_row(row, sanitize_name=True))


def _map_row(row: dict[str, Any], sanitize_name: bool) -> list[Any]:
    name_value = row.get("Name") or ""
    if sanitize_name:
        name_value = str(name_value).replace(",", "")

    return [
        row.get("acctno") or "",
        name_value,
        row.get("mnem_code") or "",
        row.get("Credit") or 0,
        row.get("Debit") or 0,
        row.get("txn_time") or "",
        row.get("trmlid") or "",
        row.get("refno") or "",
        row.get("external_refno") or "",
        row.get("remarks1") or "",
    ]


def compute_summaries(row_list: list[list[Any]]) -> dict[str, float | int]:
    credit_values = [_to_float(row[3]) for row in row_list]
    debit_values = [_to_float(row[4]) for row in row_list]

    credit_count = sum(1 for amount in credit_values if amount > 0)
    debit_count = sum(1 for amount in debit_values if amount > 0)
    credit_sum = sum(credit_values)
    debit_sum = sum(debit_values)

    return {
        "credit_count": credit_count,
        "debit_count": debit_count,
        "credit_sum": credit_sum,
        "debit_sum": debit_sum,
        "txn_count": len(row_list),
        # Assumption: net amount follows credit minus debit pattern.
        "net_amount": credit_sum - debit_sum,
    }


def _to_float(value: Any) -> float:
    try:
        return float(value or 0)
    except (TypeError, ValueError):
        return 0.0
