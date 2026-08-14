USE ecommerce_analytics;
-- Monthly KPI definition: revenue excludes created/cancelled/refunded orders.
WITH months AS (SELECT DATE_FORMAT(order_time,'%Y-%m-01') month, COUNT(*) gmv_orders, SUM(total_amount) gmv FROM orders GROUP BY 1),
paid AS (SELECT DATE_FORMAT(order_time,'%Y-%m-01') month,COUNT(*) paid_orders,COUNT(DISTINCT user_id) paying_users,SUM(total_amount) revenue FROM orders WHERE order_status IN('paid','completed') GROUP BY 1),
active AS (SELECT DATE_FORMAT(event_time,'%Y-%m-01') month,COUNT(DISTINCT user_id) mau FROM user_events GROUP BY 1)
SELECT m.month,m.gmv,p.revenue,p.paid_orders,p.paying_users,a.mau,ROUND(p.revenue/p.paid_orders,2) aov,ROUND(p.revenue/a.mau,2) arpu,ROUND(p.revenue/p.paying_users,2) arppu,ROUND(p.paying_users/a.mau,4) paying_rate FROM months m JOIN paid p USING(month) JOIN active a USING(month) ORDER BY m.month;
-- DAU and rolling 7-day WAU.
SELECT DATE(event_time) activity_date,COUNT(DISTINCT user_id) dau FROM user_events GROUP BY 1 ORDER BY 1;
-- Channel KPI segmentation.
SELECT u.channel,COUNT(DISTINCT u.user_id) registered_users,COUNT(DISTINCT o.user_id) paying_users,COUNT(o.order_id) paid_orders,ROUND(SUM(o.total_amount),2) revenue,ROUND(AVG(o.total_amount),2) aov FROM users u LEFT JOIN orders o ON u.user_id=o.user_id AND o.order_status IN('paid','completed') GROUP BY u.channel;

