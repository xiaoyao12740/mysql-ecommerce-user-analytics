-- Canonical monthly KPI export.
SELECT DATE_FORMAT(metric_date,'%Y-%m-01') month,
       SUM(paid_orders) paid_orders,
       SUM(paying_users) paying_user_days,
       ROUND(SUM(revenue),2) revenue,
       ROUND(SUM(revenue)/SUM(paid_orders),2) aov
FROM vw_daily_kpis
GROUP BY DATE_FORMAT(metric_date,'%Y-%m-01')
ORDER BY month;
