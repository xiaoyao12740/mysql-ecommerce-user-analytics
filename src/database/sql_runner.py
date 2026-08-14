"""Execute canonical SQL files; Python contains no duplicate business definitions."""
from __future__ import annotations
from pathlib import Path
import pandas as pd
from src.database.mysql_client import connect

def read_sql(path: Path) -> str:
    return path.read_text(encoding="utf-8").strip().rstrip(";")

def query_file(path: Path) -> pd.DataFrame:
    conn = connect()
    try:
        with conn.cursor() as cur:
            cur.execute(read_sql(path))
            rows = cur.fetchall()
            columns = [item[0] for item in cur.description]
        return pd.DataFrame(rows, columns=columns)
    finally:
        conn.close()

def data_quality_gate(path: Path) -> pd.DataFrame:
    report = query_file(path)
    required = {"check_name", "issue_count"}
    if not required.issubset(report.columns):
        raise RuntimeError(f"Data-quality SQL must return {sorted(required)}")
    failures = report.loc[report["issue_count"].astype(int) > 0]
    if not failures.empty:
        details = ", ".join(
            f"{row.check_name}={int(row.issue_count)}" for row in failures.itertuples()
        )
        raise RuntimeError(f"MySQL data-quality gate failed: {details}")
    print(f"MySQL data-quality gate passed: {len(report)} checks, 0 issues")
    return report

