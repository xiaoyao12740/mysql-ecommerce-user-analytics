SELECT product_id,category,buyers,units,
       ROUND(item_net_sales,2) item_net_sales,ROUND(revenue,2) revenue,
       ROUND(cost,2) cost,ROUND(gross_profit,2) gross_profit,
       ROUND(gross_margin,4) gross_margin,
       DENSE_RANK() OVER(PARTITION BY category ORDER BY revenue DESC) category_rank
FROM vw_product_performance
ORDER BY category,category_rank,product_id;
