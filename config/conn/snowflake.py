import os
from pathlib import Path

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
