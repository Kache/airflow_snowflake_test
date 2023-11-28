import logging
import os
from pathlib import Path
import sys
from snowflake.connector import SnowflakeConnection
from cryptography.hazmat.primitives import serialization

logging.basicConfig(level=logging.DEBUG, stream=sys.stdout)

_pkey = Path('~/.ssh/snowflake_key.p8').expanduser()

def test_snowflake_connector():
    p_key = serialization.load_pem_private_key(
        _pkey.read_bytes(),
        password=os.environ['SNOWFLAKE_PASSWORD'].encode(),
    )

    pkb = p_key.private_bytes(
        encoding=serialization.Encoding.DER,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption())

    connection = SnowflakeConnection(
        user=os.environ['SNOWFLAKE_USER'],
        schema=os.environ['SNOWFLAKE_SCHEMA'],
        database=os.environ['SNOWFLAKE_DATABASE'],
        account=os.environ['SNOWFLAKE_ACCOUNT'],
        warehouse=os.environ['SNOWFLAKE_WAREHOUSE'],
        region='',
        role=os.environ['SNOWFLAKE_ROLE'],
        authenticator='snowflake',
        session_parameters=None,
        application='AIRFLOW',
        private_key=pkb,
    )

    cursor = connection.cursor()
    cursor.execute("SELECT 1, 'a'")

    assert list(cursor) == [(1, 'a')]
