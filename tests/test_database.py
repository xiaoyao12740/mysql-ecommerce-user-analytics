import os,pytest
pytestmark=pytest.mark.integration
@pytest.mark.skipif(os.getenv('RUN_MYSQL_TESTS')!='1',reason='set RUN_MYSQL_TESTS=1 for MySQL integration')
def test_mysql_connection():
 from src.database.mysql_client import connect
 c=connect(); cur=c.cursor(); cur.execute('SELECT VERSION()'); assert cur.fetchone()[0].startswith('8.'); c.close()

