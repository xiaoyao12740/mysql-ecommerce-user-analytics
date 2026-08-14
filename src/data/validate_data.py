from pathlib import Path
import pandas as pd
ROOT=Path(__file__).resolve().parents[2]; RAW=ROOT/"data"/"raw"
def validate():
    t={n:pd.read_csv(RAW/f"{n}.csv") for n in ["users","products","user_events","orders","order_items","payments"]}
    assert t["users"].user_id.is_unique and t["products"].product_id.is_unique
    assert t["orders"].user_id.isin(t["users"].user_id).all()
    assert t["order_items"].order_id.isin(t["orders"].order_id).all()
    assert (t["products"].price>t["products"].cost).all() and (t["order_items"].quantity>0).all()
    calc=(t["order_items"].quantity*t["order_items"].unit_price-t["order_items"].discount).groupby(t["order_items"].order_id).sum()
    o=t["orders"].set_index("order_id"); assert ((calc-o.discount_amount+o.shipping_amount-o.total_amount).abs()<.02).all()
    return {k:len(v) for k,v in t.items()}
if __name__=="__main__": print(validate())

