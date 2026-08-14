WITH ranked AS (
  SELECT user_id,order_time,ROW_NUMBER() OVER(PARTITION BY user_id ORDER BY order_time) purchase_number,
         LAG(order_time) OVER(PARTITION BY user_id ORDER BY order_time) previous_order
  FROM vw_paid_orders
), user_summary AS (
  SELECT user_id,MAX(purchase_number) purchases,
         MAX(CASE WHEN purchase_number=2 THEN DATEDIFF(order_time,previous_order) END) days_to_second
  FROM ranked GROUP BY user_id
)
SELECT COUNT(*) buyers,SUM(purchases>=2) repeat_buyers,
       ROUND(SUM(purchases>=2)/COUNT(*),4) repeat_purchase_rate,
       ROUND(AVG(purchases),2) avg_purchase_frequency,
       ROUND(AVG(days_to_second),2) avg_days_to_second
FROM user_summary;
