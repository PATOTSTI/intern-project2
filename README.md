This project is a Python migration of the legacy VB6 report process for Virtual Mastercard transactions.

## Purpose

The program generates:
- one `.xls` report file
- one `.csv` report file

for a user-selected report date, using transaction data from the local SQLite database.

## Prerequisites

- Python 3.10 or newer
- `pip` (Python package installer)
- Project files in this repository, including:
  - `main.py`
  - `virtual_mc/`
  - `VB6 FILE/` (contains SQL create/insert scripts)

## Install Dependencies

From the project root:

```bash
pip install xlwt
```

## How to Run

Run from the project root folder.

### Option 1: Interactive date input

```bash
python main.py
```

The program will prompt:

`Enter the report date (YYYY-MM-DD):`

### Option 2: Pass date directly in command

```bash
python main.py --report-date 2026-03-13
```

### Optional arguments

- `--branch` (default: `000`)
- `--db-path` (default: `Database/TestDB.db`)
- `--output-dir` (default: `output`)

Example:

```bash
python main.py --report-date 2026-03-13 --branch 000 --output-dir output
```

## Output Structure

For each run, files are created inside a date folder:

`output/YYYYMMDD/`

Example:

`output/20260313/_virtual_mastercard_20260313.csv`

`output/20260313/_virtual_mastercard_20260313.xls`

If the `.xls` file for that date already exists, generation is skipped to avoid duplicates.

## Simple Program Flow

1. User enters a report date (interactive prompt or `--report-date`).
2. App validates and parses the date (`YYYY-MM-DD`).
3. App opens SQLite database (`Database/TestDB.db` by default).
4. If needed, app bootstraps database objects from SQL scripts in `VB6 FILE/`.
5. App prepares report parameters (month and branch support tables).
6. App queries `vwd_hm_virtual_mc` with `WHERE txn_date = <input date>`.
7. App writes `.xls` and `.csv` outputs into `output/YYYYMMDD/`.
8. App prints summary in terminal (report date, row count, file paths).

## Notes

- Date filtering now uses the exact date entered by the user.
- This implementation no longer uses previous-business-day logic.
- Date format must be `YYYY-MM-DD`.
