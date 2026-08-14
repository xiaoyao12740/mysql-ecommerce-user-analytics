USE ecommerce_analytics;
-- LAG/LEAD reveal adjacent behavior transitions inside each session.
WITH seq AS (SELECT event_type,LEAD(event_type) OVER(PARTITION BY session_id ORDER BY event_time,event_id) next_event FROM user_events), counts AS (SELECT event_type,next_event,COUNT(*) transitions FROM seq WHERE next_event IS NOT NULL GROUP BY 1,2)
SELECT event_type,next_event,transitions,ROUND(transitions/SUM(transitions) OVER(PARTITION BY event_type),4) transition_rate FROM counts ORDER BY transitions DESC;
-- Session engagement and conversion.
SELECT session_id,COUNT(*) events_per_session,COUNT(DISTINCT product_id) products_per_session,MAX(event_type='payment') converted FROM user_events GROUP BY session_id;

