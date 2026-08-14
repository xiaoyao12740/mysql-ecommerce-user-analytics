# Query optimization evidence

`sql/12_performance_optimization.sql` contains three reproducible `EXPLAIN ANALYZE` cases. The composite indexes match the leading equality column and trailing time range: `user_events(user_id,event_time)` and `orders(user_id,order_time)`. This changes eligible access from a full scan to indexed range/ref access. Exact execution plans depend on generated scale and MySQL statistics; no fabricated timing is reported.

