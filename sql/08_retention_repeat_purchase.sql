USE ecommerce_analytics;
-- Monthly registration cohort retention using event activity.
WITH cohort AS (SELECT user_id,DATE_FORMAT(signup_date,'%Y-%m-01') cohort_month FROM users), activity AS (SELECT DISTINCT user_id,DATE_FORMAT(event_time,'%Y-%m-01') activity_month FROM user_events), cells AS (SELECT c.cohort_month,a.activity_month,TIMESTAMPDIFF(MONTH,c.cohort_month,a.activity_month) month_number,COUNT(*) active_users FROM cohort c JOIN activity a USING(user_id) GROUP BY 1,2,3), sizes AS (SELECT cohort_month,COUNT(*) cohort_size FROM cohort GROUP BY 1)
SELECT x.cohort_month,x.month_number,x.active_users,s.cohort_size,ROUND(x.active_users/s.cohort_size,4) retention_rate FROM cells x JOIN sizes s USING(cohort_month) WHERE month_number>=0 ORDER BY 1,2;
-- Repeat purchase and days to second order (ROW_NUMBER + LAG).
WITH ranked AS (SELECT user_id,order_time,ROW_NUMBER() OVER(PARTITION BY user_id ORDER BY order_time) purchase_number,LAG(order_time) OVER(PARTITION BY user_id ORDER BY order_time) previous_order FROM orders WHERE order_status IN('paid','completed')), agg AS (SELECT user_id,MAX(purchase_number) purchases,MAX(CASE WHEN purchase_number=2 THEN DATEDIFF(order_time,previous_order) END) days_to_second FROM ranked GROUP BY user_id)
SELECT COUNT(*) buyers,SUM(purchases>=2) repeat_buyers,ROUND(SUM(purchases>=2)/COUNT(*),4) repeat_purchase_rate,ROUND(AVG(purchases),2) avg_purchase_frequency,ROUND(AVG(days_to_second),2) avg_days_to_second FROM agg;

