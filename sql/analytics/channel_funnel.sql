WITH f AS (
  SELECT u.channel,e.user_id,MAX(e.event_type='view') viewed,
         MAX(e.event_type='add_to_cart') carted,MAX(e.event_type='purchase') purchased,
         MAX(e.event_type='payment') paid
  FROM user_events e JOIN users u USING(user_id) GROUP BY u.channel,e.user_id
)
SELECT channel,SUM(viewed) view_users,SUM(carted) cart_users,
       SUM(purchased) purchase_users,SUM(paid) paid_users,
       ROUND(SUM(paid)/NULLIF(SUM(viewed),0),4) overall_cvr
FROM f GROUP BY channel ORDER BY channel;
