from pathlib import Path
import pandas as pd
from sqlalchemy import create_engine
from src.database.mysql_client import config
ROOT=Path(__file__).resolve().parents[2]; OUT=ROOT/"reports/tables"
QUERIES={
"daily_kpis":"SELECT * FROM vw_daily_kpis ORDER BY metric_date",
"monthly_kpis":"SELECT DATE_FORMAT(metric_date,'%%Y-%%m-01') month,SUM(paid_orders) paid_orders,SUM(paying_users) paying_user_days,ROUND(SUM(revenue),2) revenue,ROUND(SUM(revenue)/SUM(paid_orders),2) aov FROM vw_daily_kpis GROUP BY 1 ORDER BY 1",
"conversion_funnel":"WITH f AS (SELECT user_id,MAX(event_type='view') v,MAX(event_type='add_to_cart') c,MAX(event_type='purchase') p,MAX(event_type='payment') pay FROM user_events GROUP BY user_id) SELECT SUM(v) view_users,SUM(c) cart_users,SUM(p) purchase_users,SUM(pay) paid_users,ROUND(SUM(c)/SUM(v),4) view_cart_cvr,ROUND(SUM(p)/SUM(c),4) cart_purchase_cvr,ROUND(SUM(pay)/SUM(p),4) purchase_payment_cvr,ROUND(SUM(pay)/SUM(v),4) overall_cvr FROM f",
"channel_funnel":"WITH f AS (SELECT u.channel,e.user_id,MAX(e.event_type='view') v,MAX(e.event_type='add_to_cart') c,MAX(e.event_type='purchase') p,MAX(e.event_type='payment') pay FROM user_events e JOIN users u USING(user_id) GROUP BY 1,2) SELECT channel,SUM(v) view_users,SUM(c) cart_users,SUM(p) purchase_users,SUM(pay) paid_users,ROUND(SUM(pay)/SUM(v),4) overall_cvr FROM f GROUP BY channel",
"retention_cohort":"WITH c AS (SELECT user_id,DATE_FORMAT(signup_date,'%%Y-%%m-01') cohort_month FROM users),a AS (SELECT DISTINCT user_id,DATE_FORMAT(event_time,'%%Y-%%m-01') activity_month FROM user_events),x AS (SELECT c.cohort_month,TIMESTAMPDIFF(MONTH,c.cohort_month,a.activity_month) month_number,COUNT(*) active_users FROM c JOIN a USING(user_id) GROUP BY 1,2),s AS (SELECT cohort_month,COUNT(*) cohort_size FROM c GROUP BY 1) SELECT x.*,s.cohort_size,ROUND(active_users/cohort_size,4) retention_rate FROM x JOIN s USING(cohort_month) WHERE month_number>=0 ORDER BY 1,2",
"rfm_segments":"SELECT rfm_segment segment,COUNT(*) users,ROUND(SUM(monetary),2) revenue,ROUND(AVG(monetary/frequency),2) aov,ROUND(AVG(frequency),2) avg_frequency FROM vw_rfm_segments GROUP BY rfm_segment ORDER BY revenue DESC",
"product_performance":"SELECT product_id,category,buyers,units,ROUND(revenue,2) revenue,DENSE_RANK() OVER(PARTITION BY category ORDER BY revenue DESC) category_rank FROM vw_product_performance ORDER BY revenue DESC",
"repeat_purchase":"WITH r AS (SELECT user_id,order_time,ROW_NUMBER() OVER(PARTITION BY user_id ORDER BY order_time) n,LAG(order_time) OVER(PARTITION BY user_id ORDER BY order_time) prev FROM vw_paid_orders),a AS (SELECT user_id,MAX(n) purchases,MAX(CASE WHEN n=2 THEN DATEDIFF(order_time,prev) END) days_to_second FROM r GROUP BY user_id) SELECT COUNT(*) buyers,SUM(purchases>=2) repeat_buyers,ROUND(SUM(purchases>=2)/COUNT(*),4) repeat_purchase_rate,ROUND(AVG(purchases),2) avg_purchase_frequency,ROUND(AVG(days_to_second),2) avg_days_to_second FROM a",
"behavior_transitions":"WITH s AS (SELECT event_type,LEAD(event_type) OVER(PARTITION BY session_id ORDER BY event_time,event_id) next_event FROM user_events),c AS (SELECT event_type,next_event,COUNT(*) transitions FROM s WHERE next_event IS NOT NULL GROUP BY 1,2) SELECT *,ROUND(transitions/SUM(transitions) OVER(PARTITION BY event_type),4) transition_rate FROM c ORDER BY transitions DESC"
}
def engine():
 c=config(); return create_engine(f"mysql+pymysql://{c['user']}:{c['password']}@{c['host']}:{c['port']}/{c['database']}?charset=utf8mb4")
def export():
 OUT.mkdir(parents=True,exist_ok=True); e=engine(); result={}
 for name,q in QUERIES.items():
  df=pd.read_sql(q,e); df.to_csv(OUT/f"{name}.csv",index=False); result[name]=df
 return result
if __name__=="__main__": print({k:len(v) for k,v in export().items()})
