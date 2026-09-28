"""Generate the reproducible synthetic dataset used by the investigation."""

from __future__ import annotations

import csv
from datetime import date, timedelta
from pathlib import Path
import random

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"


def write_csv(name: str, rows: list[dict[str, object]]) -> None:
    path = DATA_DIR / name
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    random.seed(42)
    DATA_DIR.mkdir(exist_ok=True)

    locations = [
        {"location_id": 1, "location_name": "North Hub", "region": "North"},
        {"location_id": 2, "location_name": "Central Hub", "region": "Central"},
        {"location_id": 3, "location_name": "South Hub", "region": "South"},
        {"location_id": 4, "location_name": "Coastal Hub", "region": "East"},
    ]
    products = []
    categories = ["Safety", "Mobility", "Recovery", "Training"]
    for product_id in range(1, 17):
        category = categories[(product_id - 1) // 4]
        base_price = 28 + (product_id % 4) * 17 + categories.index(category) * 6
        products.append({
            "product_id": product_id,
            "product_name": f"{category} Product {product_id:02d}",
            "category": category,
            "unit_price": base_price,
            "unit_cost": round(base_price * random.uniform(0.43, 0.61), 2),
        })
    customers = [
        {"customer_id": customer_id, "segment": random.choice(["Small Business", "Mid-Market", "Enterprise"]), "home_region": random.choice(["North", "Central", "South", "East"])}
        for customer_id in range(1, 241)
    ]

    orders: list[dict[str, object]] = []
    items: list[dict[str, object]] = []
    returns: list[dict[str, object]] = []
    monthly_costs: list[dict[str, object]] = []
    order_id = item_id = return_id = 1

    for month in range(18):
        month_start = date(2024 + month // 12, month % 12 + 1, 1)
        for location in locations:
            # South develops a cost problem; Coastal relies increasingly on discounting.
            fixed_cost = 3000 + location["location_id"] * 500 + random.randint(-250, 250)
            if location["location_id"] == 3 and month >= 9:
                fixed_cost += 3500 + (month - 9) * 300
            monthly_costs.append({"location_id": location["location_id"], "month_start": month_start.isoformat(), "operating_cost": fixed_cost})

        for _ in range(135):
            location_id = random.randint(1, 4)
            customer_id = random.randint(1, len(customers))
            order_date = month_start + timedelta(days=random.randint(0, 27))
            orders.append({"order_id": order_id, "order_date": order_date.isoformat(), "customer_id": customer_id, "location_id": location_id})
            for _ in range(random.randint(1, 4)):
                product = random.choice(products)
                quantity = random.randint(1, 5)
                discount = random.choice([0, 0, 0.05, 0.10])
                if location_id == 4 and month >= 8:
                    discount = random.choice([0.10, 0.15, 0.20, 0.25])
                items.append({"order_item_id": item_id, "order_id": order_id, "product_id": product["product_id"], "quantity": quantity, "unit_price": product["unit_price"], "discount_pct": discount})
                return_chance = 0.035
                if product["category"] == "Recovery" and month >= 10:
                    return_chance = 0.15
                if random.random() < return_chance:
                    returns.append({"return_id": return_id, "order_item_id": item_id, "return_date": (order_date + timedelta(days=random.randint(3, 21))).isoformat(), "quantity_returned": random.randint(1, quantity), "reason": random.choice(["Damaged", "Not as expected", "Wrong item"])})
                    return_id += 1
                item_id += 1
            order_id += 1

    for name, rows in [
        ("locations.csv", locations), ("products.csv", products), ("customers.csv", customers),
        ("orders.csv", orders), ("order_items.csv", items), ("returns.csv", returns),
        ("monthly_costs.csv", monthly_costs),
    ]:
        write_csv(name, rows)
    print(f"Generated {len(orders):,} orders and {len(items):,} order lines.")


if __name__ == "__main__":
    main()
