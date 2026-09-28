-- 1. Monthly company performance: revenue can remain stable while contribution falls.
WITH line_finance AS (
  SELECT strftime('%Y-%m-01', o.order_date) AS month_start,
         oi.quantity * oi.unit_price AS gross_revenue,
         oi.quantity * oi.unit_price * oi.discount_pct AS discount_value,
         oi.quantity * p.unit_cost AS product_cost,
         COALESCE(r.quantity_returned, 0) * oi.unit_price * (1 - oi.discount_pct) AS return_value
  FROM orders o
  JOIN order_items oi ON oi.order_id = o.order_id
  JOIN products p ON p.product_id = oi.product_id
  LEFT JOIN returns r ON r.order_item_id = oi.order_item_id
), monthly_sales AS (
  SELECT month_start,
         SUM(gross_revenue - discount_value - return_value) AS net_revenue,
         SUM(gross_revenue - discount_value - return_value - product_cost) AS gross_margin
  FROM line_finance GROUP BY month_start
), monthly_overhead AS (
  SELECT month_start, SUM(operating_cost) AS operating_cost
  FROM monthly_costs GROUP BY month_start
)
SELECT s.month_start, ROUND(s.net_revenue, 2) AS net_revenue,
       ROUND(s.gross_margin - h.operating_cost, 2) AS contribution,
       ROUND(100.0 * (s.gross_margin - h.operating_cost) / s.net_revenue, 2) AS contribution_margin_pct
FROM monthly_sales s JOIN monthly_overhead h USING (month_start)
ORDER BY s.month_start;

-- 2. Location diagnosis with ranking and period-over-period comparison.
WITH location_month AS (
  SELECT l.location_name, strftime('%Y-%m-01', o.order_date) AS month_start,
         SUM(oi.quantity * oi.unit_price * (1 - oi.discount_pct)) AS discounted_sales,
         AVG(oi.discount_pct) AS average_discount
  FROM orders o JOIN locations l USING (location_id)
  JOIN order_items oi USING (order_id)
  GROUP BY l.location_name, month_start
)
SELECT location_name, month_start, ROUND(discounted_sales, 2) AS discounted_sales,
       ROUND(average_discount * 100, 2) AS average_discount_pct,
       RANK() OVER (PARTITION BY month_start ORDER BY average_discount DESC) AS discount_rank
FROM location_month ORDER BY month_start, discount_rank;

-- 3. Product-category return rate isolates the emerging product-mix problem.
SELECT p.category, SUM(oi.quantity) AS units_sold,
       COALESCE(SUM(r.quantity_returned), 0) AS units_returned,
       ROUND(100.0 * COALESCE(SUM(r.quantity_returned), 0) / SUM(oi.quantity), 2) AS return_rate_pct
FROM order_items oi JOIN products p USING (product_id)
LEFT JOIN returns r USING (order_item_id)
GROUP BY p.category ORDER BY return_rate_pct DESC;

