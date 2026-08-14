from pathlib import Path
import os, pymysql
from dotenv import load_dotenv
ROOT=Path(__file__).resolve().parents[2]; load_dotenv(ROOT/".env")
def config(database=True):
    d=dict(host=os.getenv("MYSQL_HOST","127.0.0.1"),port=int(os.getenv("MYSQL_PORT","3307")),user=os.getenv("MYSQL_USER","ecommerce_user"),password=os.getenv("MYSQL_PASSWORD","local_demo_password"),charset="utf8mb4",autocommit=True)
    if database:d["database"]=os.getenv("MYSQL_DATABASE","ecommerce_analytics")
    return d
def connect(database=True): return pymysql.connect(**config(database))
def execute_file(path):
    sql=Path(path).read_text(encoding="utf-8"); conn=connect(database="00_create_database" not in str(path))
    try:
        with conn.cursor() as cur:
            for statement in [s.strip() for s in sql.split(";") if s.strip()]: cur.execute(statement)
    finally: conn.close()

