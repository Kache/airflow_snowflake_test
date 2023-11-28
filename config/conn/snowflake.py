import os
from pathlib import Path

from cryptography.hazmat.primitives import serialization

_pkey = Path('~/.ssh/snowflake_key.p8').expanduser()

info = {
    'conn_type': 'snowflake',
    'login':     os.environ['SNOWFLAKE_USER'],
    'password':  os.environ['SNOWFLAKE_PASSWORD'],
    'host':      os.environ['SNOWFLAKE_ACCOUNT'] + '.snowflakecomputing.com',
    'schema':    os.environ['SNOWFLAKE_DATABASE'] + '/' + os.environ['SNOWFLAKE_SCHEMA'],
    'extra': {k: v for k, v in {
        'warehouse':        os.getenv('SNOWFLAKE_WAREHOUSE'),
        'role':             os.getenv('SNOWFLAKE_ROLE'),
        'account':          os.environ['SNOWFLAKE_ACCOUNT'],
        'private_key_file': str(_pkey) if _pkey.exists() else None,
    }.items() if v},
}

args = dict(
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
    private_key=serialization.load_pem_private_key(
        _pkey.read_bytes(),
        password=os.environ['SNOWFLAKE_PASSWORD'].encode(),
    ).private_bytes(
        encoding=serialization.Encoding.DER,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    ),
)
