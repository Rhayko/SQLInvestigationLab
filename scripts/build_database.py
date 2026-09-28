"""Load the generated CSV files into a constrained SQLite database."""

from __future__ import annotations

import csv
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
DATABASE_PATH = DATA_DIR / "investigation.db"


def main() -> None:
    if DATABASE_PATH.exists():
        DATABASE_PATH.unlink()
    connection = sqlite3.connect(DATABASE_PATH)
    connection.execute("PRAGMA foreign_keys = ON")
    connection.executescript((ROOT / "sql" / "01_schema.sql").read_text())

    tables = ["locations", "products", "customers", "orders", "order_items", "returns", "monthly_costs"]
    for table in tables:
        with (DATA_DIR / f"{table}.csv").open(encoding="utf-8") as handle:
            rows = list(csv.DictReader(handle))
        columns = list(rows[0])
        placeholders = ", ".join("?" for _ in columns)
        connection.executemany(
            f"INSERT INTO {table} ({', '.join(columns)}) VALUES ({placeholders})",
            [[row[column] for column in columns] for row in rows],
        )
    connection.commit()
    connection.close()
    print(f"Built {DATABASE_PATH}")


if __name__ == "__main__":
    main()
