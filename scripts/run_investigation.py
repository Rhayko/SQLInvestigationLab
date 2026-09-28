"""Execute the investigation queries and save decision-ready outputs."""
from pathlib import Path
import sqlite3
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs" / "generated"

def main():
    OUT.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(ROOT / "data" / "investigation.db")
    sql = (ROOT / "sql" / "02_investigation.sql").read_text()
    statements = [part.strip() for part in sql.split(";") if part.strip()]
    names = ["monthly_performance", "location_discount_ranking", "category_returns"]
    frames = {}
    for name, statement in zip(names, statements):
        frame = pd.read_sql_query(statement, con)
        frame.to_csv(OUT / f"{name}.csv", index=False)
        frames[name] = frame
    con.close()
    monthly = frames["monthly_performance"]
    ax = monthly.plot(x="month_start", y=["net_revenue", "contribution"], figsize=(10, 5), color=["#3d7ea6", "#b65d54"])
    ax.set(title="Stable revenue, declining contribution", xlabel="Month", ylabel="Dollars")
    ax.grid(alpha=.2); plt.xticks(rotation=45); plt.tight_layout()
    plt.savefig(OUT / "monthly_performance.png", dpi=150); plt.close()
    print(f"Wrote investigation outputs to {OUT}")

if __name__ == "__main__": main()
