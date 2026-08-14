USE ecommerce_analytics;
-- Product economics plus per-category Top-N using DENSE_RANK.
WITH perf AS (SELECT p.product_id,p.category,p.brand,COUNT(DISTINCT o.user_id) buyers,SUM(i.quantity) units,SUM(i.quantity*i.unit_price-i.discount) revenue,SUM(i.quantity*p.cost) cost FROM order_items i JOIN products p USING(product_id) JOIN orders o USING(order_id) WHERE o.order_status IN('paid','completed') GROUP BY 1,2,3), ranked AS (SELECT perf.*,revenue-cost gross_profit,ROUND((revenue-cost)/revenue,4) gross_margin,DENSE_RANK() OVER(PARTITION BY category ORDER BY revenue DESC) category_rank FROM perf)
SELECT product_id,category,brand,buyers,units,ROUND(revenue,2) revenue,ROUND(gross_profit,2) gross_profit,gross_margin,category_rank FROM ranked WHERE category_rank<=5 ORDER BY category,category_rank;

