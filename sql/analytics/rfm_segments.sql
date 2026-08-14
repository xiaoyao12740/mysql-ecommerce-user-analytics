-- RFM scores come from the deterministic view; user_id breaks NTILE ties.
SELECT rfm_segment segment,COUNT(*) users,ROUND(SUM(monetary),2) revenue,
       ROUND(AVG(monetary/frequency),2) aov,ROUND(AVG(frequency),2) avg_frequency
FROM vw_rfm_segments GROUP BY rfm_segment ORDER BY revenue DESC;
