CREATE TABLE locations (
  location_id INTEGER PRIMARY KEY,
  location_name TEXT NOT NULL UNIQUE,
  region TEXT NOT NULL
);
CREATE TABLE products (
  product_id INTEGER PRIMARY KEY,
  product_name TEXT NOT NULL,
  category TEXT NOT NULL,
  unit_price REAL NOT NULL CHECK (unit_price > 0),
  unit_cost REAL NOT NULL CHECK (unit_cost >= 0)
);
CREATE TABLE customers (
  customer_id INTEGER PRIMARY KEY,
  segment TEXT NOT NULL,
  home_region TEXT NOT NULL
);
CREATE TABLE orders (
  order_id INTEGER PRIMARY KEY,
  order_date TEXT NOT NULL,
  customer_id INTEGER NOT NULL REFERENCES customers(customer_id),
  location_id INTEGER NOT NULL REFERENCES locations(location_id)
);
CREATE TABLE order_items (
  order_item_id INTEGER PRIMARY KEY,
  order_id INTEGER NOT NULL REFERENCES orders(order_id),
  product_id INTEGER NOT NULL REFERENCES products(product_id),
  quantity INTEGER NOT NULL CHECK (quantity > 0),
  unit_price REAL NOT NULL CHECK (unit_price > 0),
  discount_pct REAL NOT NULL CHECK (discount_pct BETWEEN 0 AND 1)
);
CREATE TABLE returns (
  return_id INTEGER PRIMARY KEY,
  order_item_id INTEGER NOT NULL REFERENCES order_items(order_item_id),
  return_date TEXT NOT NULL,
  quantity_returned INTEGER NOT NULL CHECK (quantity_returned > 0),
  reason TEXT NOT NULL
);
CREATE TABLE monthly_costs (
  location_id INTEGER NOT NULL REFERENCES locations(location_id),
  month_start TEXT NOT NULL,
  operating_cost REAL NOT NULL CHECK (operating_cost >= 0),
  PRIMARY KEY (location_id, month_start)
);
CREATE INDEX idx_orders_date ON orders(order_date);
CREATE INDEX idx_orders_location ON orders(location_id);
CREATE INDEX idx_items_order ON order_items(order_id);
CREATE INDEX idx_returns_item ON returns(order_item_id);

