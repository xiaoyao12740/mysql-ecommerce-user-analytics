USE ecommerce_analytics;
-- ROW_NUMBER/LAG: purchase sequence and intervals.
SELECT user_id,order_id,order_time,ROW_NUMBER() OVER(PARTITION BY user_id ORDER BY order_time) purchase_number,DATEDIFF(order_time,LAG(order_time) OVER(PARTITION BY user_id ORDER BY order_time)) days_since_previous FROM orders WHERE order_status IN('paid','completed');
-- SUM OVER / AVG OVER / LAG: cumulative, rolling and MoM revenue.
WITH daily AS (SELECT DATE(order_time) dt,SUM(total_amount) revenue FROM orders WHERE order_status IN('paid','completed') GROUP BY 1)
SELECT dt,revenue,SUM(revenue) OVER(ORDER BY dt) cumulative_revenue,SUM(revenue) OVER(ORDER BY dt ROWS BETWEEN 6 PRECEDING AND CURRENT ROW) rolling_7d_revenue,AVG(revenue) OVER(ORDER BY dt ROWS BETWEEN 6 PRECEDING AND CURRENT ROW) rolling_7d_average FROM daily;

