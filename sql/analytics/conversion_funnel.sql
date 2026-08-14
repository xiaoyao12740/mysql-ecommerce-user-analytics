-- Reach funnel: a user counts once if they reached a stage at any time in the period.
WITH f AS (
  SELECT user_id,
         MAX(event_type='view') viewed,
         MAX(event_type='add_to_cart') carted,
         MAX(event_type='purchase') purchased,
         MAX(event_type='payment') paid
  FROM user_events GROUP BY user_id
)
SELECT SUM(viewed) view_users, SUM(carted) cart_users,
       SUM(purchased) purchase_users, SUM(paid) paid_users,
       ROUND(SUM(carted)/NULLIF(SUM(viewed),0),4) view_cart_cvr,
       ROUND(SUM(purchased)/NULLIF(SUM(carted),0),4) cart_purchase_cvr,
       ROUND(SUM(paid)/NULLIF(SUM(purchased),0),4) purchase_payment_cvr,
       ROUND(SUM(paid)/NULLIF(SUM(viewed),0),4) overall_cvr
FROM f;
