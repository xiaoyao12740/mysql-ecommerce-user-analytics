WITH sequence AS (
  SELECT event_type,LEAD(event_type) OVER(PARTITION BY session_id ORDER BY event_time,event_id) next_event
  FROM user_events
), counts AS (
  SELECT event_type,next_event,COUNT(*) transitions FROM sequence
  WHERE next_event IS NOT NULL GROUP BY event_type,next_event
)
SELECT event_type,next_event,transitions,
       ROUND(transitions/SUM(transitions) OVER(PARTITION BY event_type),4) transition_rate
FROM counts ORDER BY transitions DESC,event_type,next_event;
