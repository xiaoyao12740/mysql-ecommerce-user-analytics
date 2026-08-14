-- Every query should return zero; UNION ALL provides an auditable quality report.
SELECT 'duplicate_users' check_name, COUNT(*) issue_count FROM (SELECT user_id FROM users GROUP BY user_id HAVING COUNT(*)>1) x
UNION ALL SELECT 'null_user_fields',COUNT(*) FROM users WHERE signup_date IS NULL OR channel IS NULL
UNION ALL SELECT 'invalid_event_user',COUNT(*) FROM user_events e LEFT JOIN users u ON e.user_id=u.user_id WHERE u.user_id IS NULL
UNION ALL SELECT 'invalid_event_product',COUNT(*) FROM user_events e LEFT JOIN products p ON e.product_id=p.product_id WHERE e.product_id IS NOT NULL AND p.product_id IS NULL
UNION ALL SELECT 'event_before_signup',COUNT(*) FROM user_events e JOIN users u ON e.user_id=u.user_id WHERE DATE(e.event_time)<u.signup_date
UNION ALL SELECT 'orphan_order_item',COUNT(*) FROM order_items i LEFT JOIN orders o ON i.order_id=o.order_id WHERE o.order_id IS NULL
UNION ALL SELECT 'orphan_payment',COUNT(*) FROM payments p LEFT JOIN orders o ON p.order_id=o.order_id WHERE o.order_id IS NULL
UNION ALL SELECT 'invalid_money_or_quantity',COUNT(*) FROM order_items WHERE unit_price<=0 OR quantity<=0 OR discount<0
UNION ALL SELECT 'payment_status_mismatch',COUNT(*) FROM payments p JOIN orders o ON p.order_id=o.order_id WHERE (p.payment_status='refunded')<>(o.order_status='refunded')
UNION ALL SELECT 'payment_after_dataset_end',COUNT(*) FROM payments WHERE payment_time>'2025-12-31 23:59:59'
UNION ALL SELECT 'order_after_dataset_end',COUNT(*) FROM orders WHERE order_time>'2025-12-31 23:59:59'
UNION ALL SELECT 'event_after_dataset_end',COUNT(*) FROM user_events WHERE event_time>'2025-12-31 23:59:59'
UNION ALL SELECT 'order_total_mismatch',COUNT(*) FROM orders o JOIN (SELECT order_id,ROUND(SUM(quantity*unit_price-discount),2) item_total FROM order_items GROUP BY order_id) i ON o.order_id=i.order_id WHERE ABS(o.total_amount-(i.item_total-o.discount_amount+o.shipping_amount))>.02;
