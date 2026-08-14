USE ecommerce_analytics;
CREATE INDEX idx_users_signup ON users(signup_date); CREATE INDEX idx_users_channel ON users(channel);
CREATE INDEX idx_events_user_time ON user_events(user_id,event_time); CREATE INDEX idx_events_type_time ON user_events(event_type,event_time); CREATE INDEX idx_events_product_time ON user_events(product_id,event_time); CREATE INDEX idx_events_session ON user_events(session_id);
CREATE INDEX idx_orders_user_time ON orders(user_id,order_time); CREATE INDEX idx_orders_status_time ON orders(order_status,order_time);
CREATE INDEX idx_items_order ON order_items(order_id); CREATE INDEX idx_items_product ON order_items(product_id);
CREATE INDEX idx_payments_status_time ON payments(payment_status,payment_time);

