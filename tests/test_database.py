import os
from pathlib import Path
import pytest
from src.database.mysql_client import connect
from src.database.sql_runner import data_quality_gate, query_file

ROOT = Path(__file__).resolve().parents[1]
pytestmark=pytest.mark.integration

@pytest.mark.skipif(os.getenv('RUN_MYSQL_TESTS')!='1',reason='set RUN_MYSQL_TESTS=1 for MySQL integration')
def test_mysql_connection():
 c=connect(); cur=c.cursor(); cur.execute('SELECT VERSION()'); assert cur.fetchone()[0].startswith('8.'); c.close()

@pytest.mark.skipif(os.getenv('RUN_MYSQL_TESTS')!='1',reason='set RUN_MYSQL_TESTS=1 for MySQL integration')
def test_schema_foreign_keys_and_views():
    conn = connect()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema=DATABASE()")
            objects = {row[0] for row in cur.fetchall()}
            assert {"users","products","user_events","orders","order_items","payments"} <= objects
            assert {"vw_daily_kpis","vw_paid_orders","vw_product_performance","vw_rfm_segments","vw_user_profile"} <= objects
            cur.execute("SELECT COUNT(*) FROM information_schema.referential_constraints WHERE constraint_schema=DATABASE()")
            assert cur.fetchone()[0] >= 5
    finally:
        conn.close()

@pytest.mark.skipif(os.getenv('RUN_MYSQL_TESTS')!='1',reason='set RUN_MYSQL_TESTS=1 for MySQL integration')
def test_loaded_data_and_quality_gate():
    conn = connect()
    try:
        with conn.cursor() as cur:
            for table in ("users","products","user_events","orders","order_items","payments"):
                cur.execute(f"SELECT COUNT(*) FROM {table}")
                assert cur.fetchone()[0] > 0
    finally:
        conn.close()
    report = data_quality_gate(ROOT / "sql/03_data_quality.sql")
    assert (report["issue_count"].astype(int) == 0).all()

@pytest.mark.skipif(os.getenv('RUN_MYSQL_TESTS')!='1',reason='set RUN_MYSQL_TESTS=1 for MySQL integration')
def test_core_analytics_queries_execute():
    analytics = ROOT / "sql/analytics"
    for name in ("monthly_kpis","conversion_funnel","strict_conversion_funnel","rfm_segments"):
        result = query_file(analytics / f"{name}.sql")
        assert not result.empty
