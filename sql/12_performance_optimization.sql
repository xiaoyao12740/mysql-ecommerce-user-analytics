USE ecommerce_analytics;
-- Composite indexes match equality/range predicates and support selective joins.
EXPLAIN ANALYZE SELECT event_type,COUNT(*) FROM user_events WHERE user_id=100 AND event_time>='2025-06-01' GROUP BY event_type;
EXPLAIN ANALYZE SELECT order_id,order_time,total_amount FROM orders WHERE user_id=100 AND order_time>='2025-01-01' ORDER BY order_time;
EXPLAIN ANALYZE SELECT product_id,SUM(quantity*unit_price-discount) revenue FROM order_items WHERE product_id BETWEEN 1 AND 50 GROUP BY product_id;
