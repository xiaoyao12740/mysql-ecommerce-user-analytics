SELECT product_id,category,buyers,units,ROUND(revenue,2) revenue,
       DENSE_RANK() OVER(PARTITION BY category ORDER BY revenue DESC,product_id) category_rank
FROM vw_product_performance ORDER BY revenue DESC,product_id;
