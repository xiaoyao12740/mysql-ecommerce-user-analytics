-- Strict sequential funnel: each next stage must occur at or after the prior stage.
WITH views AS (
  SELECT user_id, MIN(event_time) view_time FROM user_events WHERE event_type='view' GROUP BY user_id
), carts AS (
  SELECT v.user_id,v.view_time,MIN(e.event_time) cart_time FROM views v
  LEFT JOIN user_events e ON e.user_id=v.user_id AND e.event_type='add_to_cart' AND e.event_time>=v.view_time
  GROUP BY v.user_id,v.view_time
), purchases AS (
  SELECT c.user_id,c.view_time,c.cart_time,MIN(e.event_time) purchase_time FROM carts c
  LEFT JOIN user_events e ON e.user_id=c.user_id AND e.event_type='purchase' AND e.event_time>=c.cart_time
  GROUP BY c.user_id,c.view_time,c.cart_time
), payments AS (
  SELECT p.user_id,p.view_time,p.cart_time,p.purchase_time,MIN(e.event_time) payment_time FROM purchases p
  LEFT JOIN user_events e ON e.user_id=p.user_id AND e.event_type='payment' AND e.event_time>=p.purchase_time
  GROUP BY p.user_id,p.view_time,p.cart_time,p.purchase_time
)
SELECT COUNT(*) view_users, COUNT(cart_time) cart_users,
       COUNT(purchase_time) purchase_users, COUNT(payment_time) paid_users,
       ROUND(COUNT(cart_time)/NULLIF(COUNT(*),0),4) view_cart_cvr,
       ROUND(COUNT(purchase_time)/NULLIF(COUNT(cart_time),0),4) cart_purchase_cvr,
       ROUND(COUNT(payment_time)/NULLIF(COUNT(purchase_time),0),4) purchase_payment_cvr,
       ROUND(COUNT(payment_time)/NULLIF(COUNT(*),0),4) overall_cvr
FROM payments;
