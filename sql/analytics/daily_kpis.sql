-- Canonical daily KPI export. Revenue excludes created/cancelled/refunded orders.
SELECT metric_date, paid_orders, paying_users, ROUND(revenue,2) revenue, ROUND(aov,2) aov
FROM vw_daily_kpis
ORDER BY metric_date;
