WITH cohort AS (
  SELECT user_id,DATE_FORMAT(signup_date,'%Y-%m-01') cohort_month FROM users
), activity AS (
  SELECT DISTINCT user_id,DATE_FORMAT(event_time,'%Y-%m-01') activity_month FROM user_events
), cells AS (
  SELECT c.cohort_month,TIMESTAMPDIFF(MONTH,c.cohort_month,a.activity_month) month_number,
         COUNT(*) active_users
  FROM cohort c JOIN activity a USING(user_id) GROUP BY 1,2
), sizes AS (
  SELECT cohort_month,COUNT(*) cohort_size FROM cohort GROUP BY 1
)
SELECT x.cohort_month,x.month_number,x.active_users,s.cohort_size,
       ROUND(x.active_users/s.cohort_size,4) retention_rate
FROM cells x JOIN sizes s USING(cohort_month)
WHERE month_number>=0 ORDER BY x.cohort_month,x.month_number;
