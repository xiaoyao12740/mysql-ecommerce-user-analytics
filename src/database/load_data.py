from pathlib import Path
import pandas as pd
from sqlalchemy import create_engine
from src.database.mysql_client import config, execute_file
ROOT=Path(__file__).resolve().parents[2]
def load():
    execute_file(ROOT/"sql/00_create_database.sql"); execute_file(ROOT/"sql/01_create_tables.sql")
    c=config(); url=f"mysql+pymysql://{c['user']}:{c['password']}@{c['host']}:{c['port']}/{c['database']}?charset=utf8mb4"; eng=create_engine(url)
    order=["users","products","orders","order_items","payments","user_events"]
    for name in order:
        df=pd.read_csv(ROOT/f"data/raw/{name}.csv");
        for col in [x for x in df.columns if x.endswith("date") or x.endswith("time") or x=="created_at"]: df[col]=pd.to_datetime(df[col])
        df.to_sql(name,eng,if_exists="append",index=False,chunksize=5000,method="multi"); print(f"loaded {name}: {len(df):,}")
    execute_file(ROOT/"sql/02_create_indexes.sql"); execute_file(ROOT/"sql/11_views.sql")
if __name__=="__main__": load()
