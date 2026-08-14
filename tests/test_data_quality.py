import pandas as pd
import pytest
from src.data.generate_data import generate

@pytest.fixture(scope="module")
def generated_dir(tmp_path_factory):
 path=tmp_path_factory.mktemp("generated_ecommerce_data")
 generate(300,42,output_dir=path)
 return path

def test_generated_relations(generated_dir):
 u=pd.read_csv(generated_dir/'users.csv'); o=pd.read_csv(generated_dir/'orders.csv'); i=pd.read_csv(generated_dir/'order_items.csv'); p=pd.read_csv(generated_dir/'products.csv')
 assert u.user_id.is_unique and o.order_id.is_unique and i.order_item_id.is_unique
 assert o.user_id.isin(u.user_id).all() and i.order_id.isin(o.order_id).all()
 assert (p.price>p.cost).all() and (i.quantity>0).all()
def test_order_totals(generated_dir):
 o=pd.read_csv(generated_dir/'orders.csv').set_index('order_id'); i=pd.read_csv(generated_dir/'order_items.csv'); calc=(i.quantity*i.unit_price-i.discount).groupby(i.order_id).sum()
 assert ((calc-o.discount_amount+o.shipping_amount-o.total_amount).abs()<.02).all()

def test_dataset_time_boundaries(generated_dir):
 events=pd.read_csv(generated_dir/'user_events.csv',parse_dates=['event_time']); orders=pd.read_csv(generated_dir/'orders.csv',parse_dates=['order_time']); payments=pd.read_csv(generated_dir/'payments.csv',parse_dates=['payment_time'])
 dataset_end=pd.Timestamp('2025-12-31 23:59:59')
 assert events.event_time.max()<=dataset_end
 assert orders.order_time.max()<=dataset_end
 assert payments.payment_time.max()<=dataset_end
