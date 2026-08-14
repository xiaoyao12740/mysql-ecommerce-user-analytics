USE ecommerce_analytics;
CREATE OR REPLACE VIEW vw_paid_orders AS SELECT order_id,user_id,order_time,total_amount FROM orders WHERE order_status IN('paid','completed');
CREATE OR REPLACE VIEW vw_daily_kpis AS SELECT DATE(order_time) metric_date,COUNT(*) paid_orders,COUNT(DISTINCT user_id) paying_users,SUM(total_amount) revenue,AVG(total_amount) aov FROM orders WHERE order_status IN('paid','completed') GROUP BY DATE(order_time);
CREATE OR REPLACE VIEW vw_product_performance AS
WITH item_base AS (
  SELECT i.order_item_id,i.order_id,i.product_id,p.category,o.user_id,i.quantity,p.cost,
         i.quantity*i.unit_price-i.discount item_net_sales,
         o.total_amount,o.discount_amount,o.shipping_amount,
         SUM(i.quantity*i.unit_price-i.discount) OVER(PARTITION BY i.order_id) order_item_net_sales
  FROM order_items i
  JOIN products p USING(product_id)
  JOIN orders o USING(order_id)
  WHERE o.order_status IN('paid','completed')
), proportional AS (
  SELECT item_base.*,
         item_net_sales
         - discount_amount*item_net_sales/NULLIF(order_item_net_sales,0)
         + shipping_amount*item_net_sales/NULLIF(order_item_net_sales,0) raw_allocated_revenue,
         quantity*cost product_cost
  FROM item_base
), rounded AS (
  SELECT proportional.*,ROUND(raw_allocated_revenue,2) rounded_revenue,
         ROW_NUMBER() OVER(PARTITION BY order_id ORDER BY order_item_id) allocation_row,
         SUM(ROUND(raw_allocated_revenue,2)) OVER(PARTITION BY order_id) rounded_order_revenue
  FROM proportional
), allocated AS (
  SELECT rounded.*,
         CASE WHEN allocation_row=1
              THEN rounded_revenue+(total_amount-rounded_order_revenue)
              ELSE rounded_revenue END allocated_revenue
  FROM rounded
)
SELECT product_id,category,COUNT(DISTINCT user_id) buyers,SUM(quantity) units,
       SUM(item_net_sales) item_net_sales,SUM(allocated_revenue) revenue,
       SUM(product_cost) cost,SUM(allocated_revenue-product_cost) gross_profit,
       SUM(allocated_revenue-product_cost)/NULLIF(SUM(allocated_revenue),0) gross_margin
FROM allocated
GROUP BY product_id,category;
CREATE OR REPLACE VIEW vw_rfm_segments AS WITH b AS (SELECT user_id,DATEDIFF((SELECT DATE(MAX(order_time)) FROM orders),DATE(MAX(order_time))) recency,COUNT(*) frequency,SUM(total_amount) monetary FROM orders WHERE order_status IN('paid','completed') GROUP BY user_id),s AS (SELECT b.*,6-NTILE(5) OVER(ORDER BY recency,user_id) r_score,NTILE(5) OVER(ORDER BY frequency,user_id) f_score,NTILE(5) OVER(ORDER BY monetary,user_id) m_score FROM b) SELECT s.*,CASE WHEN r_score>=4 AND f_score>=4 AND m_score>=4 THEN 'Champions' WHEN f_score>=4 AND m_score>=3 THEN 'Loyal Customers' WHEN r_score>=4 AND f_score BETWEEN 2 AND 3 THEN 'Potential Loyalists' WHEN r_score=5 AND f_score=1 THEN 'New Customers' WHEN r_score<=2 AND f_score>=3 THEN 'At Risk' WHEN r_score<=2 AND f_score<=2 THEN 'Hibernating' ELSE 'Other' END rfm_segment FROM s;
CREATE OR REPLACE VIEW vw_user_profile AS
WITH event_agg AS (SELECT user_id,DATE(MAX(event_time)) last_active_date,COUNT(DISTINCT DATE(event_time)) active_days,SUM(event_type='view') view_count,SUM(event_type='add_to_cart') cart_count,SUM(event_type='purchase') purchase_count FROM user_events GROUP BY user_id),
order_agg AS (SELECT user_id,COUNT(*) paid_order_count,SUM(total_amount) total_spend,AVG(total_amount) avg_order_value FROM vw_paid_orders GROUP BY user_id),
category_rank AS (SELECT o.user_id,p.category,SUM(i.quantity) units,ROW_NUMBER() OVER(PARTITION BY o.user_id ORDER BY SUM(i.quantity) DESC,p.category) rn FROM vw_paid_orders o JOIN order_items i USING(order_id) JOIN products p USING(product_id) GROUP BY o.user_id,p.category),
favorite AS (SELECT user_id,category FROM category_rank WHERE rn=1)
SELECT u.user_id,u.channel,u.region,u.device,DATEDIFF(CURDATE(),u.signup_date) tenure_days,e.last_active_date,COALESCE(e.active_days,0) active_days,COALESCE(e.view_count,0) view_count,COALESCE(e.cart_count,0) cart_count,COALESCE(e.purchase_count,0) purchase_count,COALESCE(o.paid_order_count,0) paid_order_count,COALESCE(o.total_spend,0) total_spend,COALESCE(o.avg_order_value,0) avg_order_value,f.category favorite_category,r.rfm_segment FROM users u LEFT JOIN event_agg e USING(user_id) LEFT JOIN order_agg o USING(user_id) LEFT JOIN favorite f USING(user_id) LEFT JOIN vw_rfm_segments r USING(user_id);
