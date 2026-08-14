def test_funnel_math():
 users=[{'v':1,'c':1,'p':1,'pay':1},{'v':1,'c':1,'p':0,'pay':0},{'v':1,'c':0,'p':0,'pay':0}]
 assert sum(x['pay'] for x in users)/sum(x['v'] for x in users)==1/3
def test_repeat_purchase_math():
 orders={1:2,2:1,3:3}; assert sum(v>=2 for v in orders.values())/len(orders)==2/3
def test_rfm_recency_direction():
 recency=[2,20,100]; scores=[5,3,1]; assert scores[recency.index(min(recency))]==5

