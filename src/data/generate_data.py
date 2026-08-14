"""Generate reproducible, relational e-commerce CSV data (seed=42 by default)."""
from __future__ import annotations
import argparse
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "data" / "raw"
START = pd.Timestamp("2025-01-01")
END = pd.Timestamp("2025-12-31 23:59:59")

def _dates(rng, low, high, n):
    return pd.to_datetime(rng.integers(low.value // 10**9, high.value // 10**9, n), unit="s")

def generate(users: int = 50_000, seed: int = 42, output_dir: Path | None = None) -> dict[str, int]:
    raw = Path(output_dir) if output_dir is not None else RAW
    rng = np.random.default_rng(seed); raw.mkdir(parents=True, exist_ok=True)
    n_products = max(500, min(1500, users // 25))
    channels = np.array(["organic","search","social","referral","display","affiliate"])
    channel_p = np.array([.23,.24,.19,.12,.10,.12])
    profiles = np.array(["high_value","regular","casual","price_sensitive","inactive"])
    profile_p = np.array([.08,.30,.30,.22,.10])
    signup = _dates(rng, START, pd.Timestamp("2025-10-01"), users).normalize()
    udf = pd.DataFrame({"user_id":np.arange(1,users+1),"signup_date":signup,
        "channel":rng.choice(channels,users,p=channel_p),"region":rng.choice(["East","North","South","West","Central"],users,p=[.30,.20,.22,.13,.15]),
        "device":rng.choice(["Android","iOS","Web"],users,p=[.48,.30,.22]),"age_group":rng.choice(["18-24","25-34","35-44","45-54","55+"],users,p=[.18,.36,.25,.14,.07])})
    hidden = rng.choice(profiles,users,p=profile_p)
    cats=np.array(["Electronics","Home","Beauty","Sports","Books","Food","Fashion"])
    cat=rng.choice(cats,n_products,p=[.16,.18,.14,.13,.12,.12,.15])
    base={"Electronics":500,"Home":180,"Beauty":90,"Sports":160,"Books":45,"Food":55,"Fashion":120}
    price=np.array([max(8,rng.lognormal(np.log(base[c]),.55)) for c in cat]).round(2)
    margin=rng.uniform(.18,.55,n_products)
    pdf=pd.DataFrame({"product_id":np.arange(1,n_products+1),"category":cat,"brand":[f"Brand-{x:02d}" for x in rng.integers(1,61,n_products)],
        "price":price,"cost":(price*(1-margin)).round(2),"created_at":_dates(rng,pd.Timestamp("2023-01-01"),START,n_products)})
    # Purchase propensity depends on latent profile and acquisition channel.
    # Orders are deliberately concentrated among valuable users: realistic traffic
    # has many browsers but a smaller buyer population with repeat purchases.
    lam={"high_value":15.0,"regular":5.0,"casual":.15,"price_sensitive":.08,"inactive":.01}
    cm={"organic":1.05,"search":1.20,"social":.80,"referral":1.15,"display":.72,"affiliate":1.02}
    counts=np.array([rng.poisson(lam[p]*cm[c]) for p,c in zip(hidden,udf.channel)])
    buyer_ids=np.repeat(udf.user_id.to_numpy(),counts); n_orders=len(buyer_ids)
    if n_orders:
        sd=signup[buyer_ids-1].to_numpy(dtype="datetime64[s]").astype("int64")
        hi=np.full(n_orders,END.value//10**9); span=np.maximum(1,hi-sd)
        # Earlier activity is more likely, while still retaining seasonality.
        frac=np.minimum(.999,rng.beta(1.15,1.35,n_orders)); ots=pd.to_datetime(sd+(span*frac).astype("int64"),unit="s")
        status=rng.choice(["created","paid","completed","cancelled","refunded"],n_orders,p=[.035,.12,.72,.075,.05])
        odf=pd.DataFrame({"order_id":np.arange(1,n_orders+1),"user_id":buyer_ids,"order_time":ots,"order_status":status})
        item_counts=rng.choice([1,2,3,4],n_orders,p=[.58,.27,.11,.04]); item_order=np.repeat(odf.order_id.to_numpy(),item_counts)
        item_product=rng.integers(1,n_products+1,len(item_order)); qty=rng.choice([1,2,3],len(item_order),p=[.85,.12,.03])
        unit=pdf.price.to_numpy()[item_product-1]; disc=np.where(rng.random(len(item_order))<.28,(unit*qty*rng.uniform(.03,.18,len(item_order))).round(2),0)
        idf=pd.DataFrame({"order_item_id":np.arange(1,len(item_order)+1),"order_id":item_order,"product_id":item_product,"quantity":qty,"unit_price":unit,"discount":disc})
        subtotal=(idf.quantity*idf.unit_price-idf.discount).groupby(idf.order_id).sum(); order_disc=np.where(rng.random(n_orders)<.12,rng.uniform(0,12,n_orders),0).round(2)
        shipping=np.where(subtotal.to_numpy()>=199,0,rng.choice([0,8,12,15],n_orders,p=[.12,.35,.38,.15]))
        odf["discount_amount"]=np.minimum(order_disc,subtotal.to_numpy()).round(2); odf["shipping_amount"]=shipping
        odf["total_amount"]=(subtotal.to_numpy()-odf.discount_amount+shipping).round(2)
        paymask=np.isin(status,["paid","completed","refunded"]); po=odf.loc[paymask]
        pstatus=np.where(po.order_status.eq("refunded"),"refunded","success")
        paytime=(po.order_time+pd.to_timedelta(rng.integers(1,180,len(po)),unit="m")).clip(upper=END)
        paydf=pd.DataFrame({"payment_id":np.arange(1,len(po)+1),"order_id":po.order_id.to_numpy(),"payment_time":paytime,
            "payment_method":rng.choice(["alipay","wechat","card"],len(po),p=[.42,.37,.21]),"payment_amount":po.total_amount.to_numpy(),"payment_status":pstatus})
        # Events are noisy but correlated: every user registers; orders add purchase/payment, plus browsing/cart history.
        ev=[]; eid=1
        for uid,su,dev in zip(udf.user_id,signup,udf.device): ev.append((eid,uid,su+pd.Timedelta(hours=9),"register",None,f"s{uid}-0",dev)); eid+=1
        order_prod=idf.groupby("order_id").product_id.first()
        for row in odf.itertuples():
            prod=int(order_prod.loc[row.order_id]); dev=udf.device.iloc[row.user_id-1]; sess=f"s{row.user_id}-{row.order_id}"
            # Pre-purchase browsing cannot precede registration.
            t=max(row.order_time-pd.Timedelta(minutes=int(rng.integers(8,240))), signup[row.user_id-1]+pd.Timedelta(hours=1))
            for typ,delta in [("view",0),("add_to_cart",int(rng.integers(1,30))),("purchase",int(rng.integers(31,80)))]:
                if typ!="add_to_cart" or rng.random()<.76: ev.append((eid,row.user_id,min(t+pd.Timedelta(minutes=delta),END),typ,prod,sess,dev)); eid+=1
            if row.order_status in ("paid","completed","refunded"): ev.append((eid,row.user_id,min(row.order_time+pd.Timedelta(minutes=90),END),"payment",prod,sess,dev)); eid+=1
        # Non-order sessions create realistic abandonment and favorites.
        # Fewer distinct sessions with multiple page views avoids artificially
        # inflating retention while preserving a realistic million-event scale.
        extra=int(users*4); eu=rng.integers(1,users+1,extra)
        for j,uid in enumerate(eu):
            lo=signup[uid-1]; t=_dates(rng,lo,max(lo+pd.Timedelta(days=1),END),1)[0]; prod=int(rng.integers(1,n_products+1)); sess=f"b{uid}-{j}"
            for view_n in range(int(rng.integers(3,6))):
                view_prod=prod if view_n==0 else int(rng.integers(1,n_products+1))
                ev.append((eid,uid,min(t+pd.Timedelta(minutes=view_n),END),"view",view_prod,sess,udf.device.iloc[uid-1])); eid+=1
            if rng.random()<.18: ev.append((eid,uid,min(t+pd.Timedelta(minutes=3),END),"favorite",prod,sess,udf.device.iloc[uid-1])); eid+=1
            if rng.random()<.025: ev.append((eid,uid,min(t+pd.Timedelta(minutes=5),END),"add_to_cart",prod,sess,udf.device.iloc[uid-1])); eid+=1
        edf=pd.DataFrame(ev,columns=["event_id","user_id","event_time","event_type","product_id","session_id","device"])
    for name,df in {"users":udf,"products":pdf,"orders":odf,"order_items":idf,"payments":paydf,"user_events":edf}.items(): df.to_csv(raw/f"{name}.csv",index=False)
    return {k:len(v) for k,v in {"users":udf,"products":pdf,"events":edf,"orders":odf,"order_items":idf,"payments":paydf}.items()}

def main():
    p=argparse.ArgumentParser(); p.add_argument("--users",type=int,default=50_000); p.add_argument("--seed",type=int,default=42); a=p.parse_args(); print(generate(a.users,a.seed))
if __name__=="__main__": main()
