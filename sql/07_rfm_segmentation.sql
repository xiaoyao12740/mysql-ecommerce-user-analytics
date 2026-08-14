USE ecommerce_analytics;
WITH base AS (SELECT user_id,DATEDIFF((SELECT DATE(MAX(order_time)) FROM orders),DATE(MAX(order_time))) recency,COUNT(*) frequency,SUM(total_amount) monetary FROM orders WHERE order_status IN('paid','completed') GROUP BY user_id),
scores AS (SELECT base.*,6-NTILE(5) OVER(ORDER BY recency) r_score,NTILE(5) OVER(ORDER BY frequency) f_score,NTILE(5) OVER(ORDER BY monetary) m_score FROM base),
seg AS (SELECT *,CONCAT(r_score,f_score,m_score) rfm_score,CASE WHEN r_score>=4 AND f_score>=4 AND m_score>=4 THEN 'Champions' WHEN f_score>=4 AND m_score>=3 THEN 'Loyal Customers' WHEN r_score>=4 AND f_score BETWEEN 2 AND 3 THEN 'Potential Loyalists' WHEN r_score=5 AND f_score=1 THEN 'New Customers' WHEN r_score<=2 AND f_score>=3 THEN 'At Risk' WHEN r_score<=2 AND f_score<=2 THEN 'Hibernating' ELSE 'Other' END segment FROM scores)
SELECT segment,COUNT(*) users,ROUND(SUM(monetary),2) revenue,ROUND(AVG(monetary/frequency),2) aov,ROUND(AVG(frequency),2) avg_frequency FROM seg GROUP BY segment ORDER BY revenue DESC;

