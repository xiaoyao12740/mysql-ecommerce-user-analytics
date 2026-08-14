import pandas as pd
from src.data.generate_data import generate,RAW
def test_generated_relations():
 generate(300,42); u=pd.read_csv(RAW/'users.csv'); o=pd.read_csv(RAW/'orders.csv'); i=pd.read_csv(RAW/'order_items.csv'); p=pd.read_csv(RAW/'products.csv')
 assert u.user_id.is_unique and o.order_id.is_unique and i.order_item_id.is_unique
 assert o.user_id.isin(u.user_id).all() and i.order_id.isin(o.order_id).all()
 assert (p.price>p.cost).all() and (i.quantity>0).all()
def test_order_totals():
 o=pd.read_csv(RAW/'orders.csv').set_index('order_id'); i=pd.read_csv(RAW/'order_items.csv'); calc=(i.quantity*i.unit_price-i.discount).groupby(i.order_id).sum()
 assert ((calc-o.discount_amount+o.shipping_amount-o.total_amount).abs()<.02).all()

