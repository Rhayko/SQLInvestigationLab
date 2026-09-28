import sqlite3, subprocess, sys, unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

class ProjectTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        subprocess.run([sys.executable, "scripts/generate_data.py"], cwd=ROOT, check=True)
        subprocess.run([sys.executable, "scripts/build_database.py"], cwd=ROOT, check=True)

    def test_expected_row_counts_and_foreign_keys(self):
        con = sqlite3.connect(ROOT / "data" / "investigation.db")
        self.assertEqual(con.execute("PRAGMA foreign_key_check").fetchall(), [])
        self.assertEqual(con.execute("SELECT COUNT(*) FROM orders").fetchone()[0], 2430)
        self.assertGreater(con.execute("SELECT COUNT(*) FROM order_items").fetchone()[0], 5000)
        con.close()

    def test_investigation_queries_execute(self):
        con = sqlite3.connect(ROOT / "data" / "investigation.db")
        statements = [s.strip() for s in (ROOT / "sql" / "02_investigation.sql").read_text().split(";") if s.strip()]
        self.assertEqual(len(statements), 3)
        for statement in statements: self.assertGreater(len(con.execute(statement).fetchall()), 0)
        con.close()

if __name__ == "__main__": unittest.main()

