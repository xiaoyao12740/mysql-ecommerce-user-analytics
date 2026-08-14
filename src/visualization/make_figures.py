from pathlib import Path
import pandas as pd, numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parents[2]; T=ROOT/"reports/tables"; F=ROOT/"reports/figures"
plt.style.use("seaborn-v0_8-whitegrid")
def save(name): plt.tight_layout(); plt.savefig(F/name,dpi=180,bbox_inches="tight"); plt.close()
def figures():
 F.mkdir(parents=True,exist_ok=True)
 fig,ax=plt.subplots(figsize=(11,6)); ax.axis('off')
 boxes={"users":(.05,.55),"user_events":(.38,.78),"orders":(.38,.42),"order_items":(.68,.42),"products":(.68,.75),"payments":(.68,.12)}
 for label,(x,y) in boxes.items(): ax.text(x,y,label,ha='center',va='center',fontsize=13,weight='bold',bbox=dict(boxstyle='round,pad=.55',facecolor='#EAF2F8',edgecolor='#2878B5'))
 for a,b in [("users","user_events"),("users","orders"),("orders","order_items"),("order_items","products"),("orders","payments")]:
  x1,y1=boxes[a]; x2,y2=boxes[b]; ax.annotate('',xy=(x2-.055,y2),xytext=(x1+.055,y1),arrowprops=dict(arrowstyle='->',lw=1.8,color='#555'))
 ax.set_title("E-commerce Analytics Database Schema",fontsize=17,weight='bold'); save("00_database_schema.png")
 fig,ax=plt.subplots(figsize=(13,2.4)); ax.axis('off'); ax.text(.5,.5,"Generate -> CSV Validate -> MySQL 8 Load -> DB Quality Gate -> Canonical SQL -> Export -> Visualize",ha='center',va='center',fontsize=15,weight='bold'); save("01_project_pipeline.png")
 m=pd.read_csv(T/"monthly_kpis.csv"); plt.figure(figsize=(9,4.5)); plt.plot(m.month,m.revenue,marker='o'); plt.xticks(rotation=45); plt.title("Monthly Revenue (SQL Result)"); plt.ylabel("Revenue"); save("02_monthly_gmv.png")
 f=pd.read_csv(T/"conversion_funnel.csv").iloc[0]; strict=pd.read_csv(T/"strict_conversion_funnel.csv").iloc[0]; cols=["view_users","cart_users","purchase_users","paid_users"]; labels=["View","Cart","Purchase","Payment"]; x=np.arange(len(labels)); plt.figure(figsize=(8,4.5)); plt.bar(x-.18,[f[c] for c in cols],.36,label="Reach",color="#2878B5"); plt.bar(x+.18,[strict[c] for c in cols],.36,label="Strict sequential",color="#9AC9DB"); plt.xticks(x,labels); plt.legend(); plt.title("Reach vs Strict Sequential Funnel"); save("03_conversion_funnel.png")
 c=pd.read_csv(T/"channel_funnel.csv"); plt.figure(figsize=(8,4.5)); plt.bar(c.channel,c.overall_cvr,color="#9AC9DB"); plt.title("Overall Conversion by Channel"); plt.ylabel("CVR"); save("04_channel_conversion.png")
 r=pd.read_csv(T/"retention_cohort.csv"); p=r.pivot(index="cohort_month",columns="month_number",values="retention_rate"); plt.figure(figsize=(10,5)); plt.imshow(p.fillna(np.nan),aspect='auto',cmap='Blues',vmin=0,vmax=1); plt.colorbar(label='Retention'); plt.yticks(range(len(p)),p.index); plt.xlabel("Month Number"); plt.title("Monthly Cohort Retention"); save("05_retention_cohort.png")
 s=pd.read_csv(T/"rfm_segments.csv"); plt.figure(figsize=(9,4.5)); plt.bar(s.segment,s.users,color="#F8AC8C"); plt.xticks(rotation=30,ha='right'); plt.title("RFM Segment Distribution"); save("06_rfm_segments.png")
 plt.figure(figsize=(9,4.5)); plt.bar(s.segment,s.revenue,color="#C82423"); plt.xticks(rotation=30,ha='right'); plt.title("Revenue by RFM Segment"); save("07_rfm_revenue.png")
 rp=pd.read_csv(T/"repeat_purchase.csv").iloc[0]; plt.figure(figsize=(6,4)); plt.bar(["One-time","Repeat"],[rp.buyers-rp.repeat_buyers,rp.repeat_buyers],color=["#9AC9DB","#2878B5"]); plt.title("Repeat Purchase Buyers"); save("08_repeat_purchase.png")
 pr=pd.read_csv(T/"product_performance.csv"); cat=pr.groupby('category').revenue.sum().sort_values(); plt.figure(figsize=(8,4.5)); cat.plot.barh(color="#FF8884"); plt.title("Revenue by Category"); save("09_category_revenue.png")
 top=pr.nlargest(10,'revenue').sort_values('revenue'); plt.figure(figsize=(8,5)); plt.barh(top.product_id.astype(str),top.revenue,color="#2878B5"); plt.title("Top 10 Products by Revenue"); plt.xlabel("Revenue"); save("10_top_products.png")
 b=pd.read_csv(T/"behavior_transitions.csv").head(10); plt.figure(figsize=(9,5)); plt.barh((b.event_type+' → '+b.next_event).iloc[::-1],b.transitions.iloc[::-1],color="#9AC9DB"); plt.title("Top Behavior Transitions"); save("11_user_behavior_transition.png")
 plt.figure(figsize=(8,3)); plt.axis('off'); plt.text(.5,.5,"Composite indexes align with\nequality + time-range predicates\nSee reports/metrics/query_optimization.md",ha='center',va='center',fontsize=15); save("12_query_optimization.png")
 return sorted(x.name for x in F.glob('*.png'))
if __name__=="__main__": print(figures())
