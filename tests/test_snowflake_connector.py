import logging
import sys
from snowflake.connector import SnowflakeConnection

sys.path.extend(['config', 'dags'])

import conn.snowflake
from utils import auth_snowflake

logging.basicConfig(level=logging.DEBUG, stream=sys.stdout)

def test_snowflake_connector():
    connection = SnowflakeConnection(**conn.snowflake.args)
    cursor = connection.cursor()
    cursor.execute("SELECT 1, 'a'")

    assert list(cursor) == [(1, 'a')]


def test_snowflake_auth_only():
    resp = auth_snowflake(conn.snowflake.args)
    resp.raise_for_status()
    assert resp.ok


if __name__ == '__main__':
    test_snowflake_connector()
