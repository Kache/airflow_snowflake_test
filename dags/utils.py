import gzip
import json
import urllib.parse
import uuid
from snowflake.connector.auth import AuthByKeyPair
from snowflake.connector.backoff_policies import exponential_backoff
from snowflake.connector.network import SnowflakeAuth
from snowflake.connector.vendored import requests


def auth_snowflake(args):
    # stripped down version of snowflake.connector.auth.Auth.authenticate()
    auth_instance = AuthByKeyPair(
        private_key=args['private_key'],
        timeout=5,
        backoff_generator=exponential_backoff()(),
    )

    auth_instance.prepare(
        account=args['account'],
        user=args['user'],
    )

    assert auth_instance._jwt_token

    headers = {
        'Content-Type': 'application/json',
        'accept': 'application/snowflake',
        'User-Agent': 'PythonConnector/3.5.0 (macOS-13.5.2-arm64-arm-64bit) CPython/3.11.5',
        'Content-Encoding': 'gzip',
    }
    body = {
        'data': {
            'CLIENT_APP_ID': 'PythonConnector',
            'CLIENT_APP_VERSION': '3.5.0',
            'SVN_REVISION': None,
            'ACCOUNT_NAME': args['account'],
            'LOGIN_NAME': args['user'],
            'CLIENT_ENVIRONMENT': {
                'APPLICATION': 'AIRFLOW',
                'OS': 'Darwin',
                'OS_VERSION': 'macOS-13.5.2-arm64-arm-64bit',
                'PYTHON_VERSION': '3.11.5',
                'PYTHON_RUNTIME': 'CPython',
                'PYTHON_COMPILER': 'Clang 14.0.3 (clang-1403.0.22.14.1)',
                'OCSP_MODE': 'FAIL_OPEN',
                'TRACING': 10,
                'LOGIN_TIMEOUT': None,
                'NETWORK_TIMEOUT': None,
                'SOCKET_TIMEOUT': None,
            },
            'SESSION_PARAMETERS': {'CLIENT_PREFETCH_THREADS': 4},
        },
    }
    auth_instance.update_body(body)
    url_parameters = {
        'request_id': uuid.uuid4(),
        'databaseName': args['database'],
        'schemaName': args['schema'],
        'warehouse': args['warehouse'],
        'roleName': args['role'],
    }
    url = f'/session/v1/login-request?{urllib.parse.urlencode(url_parameters)}'
    full_url = f"https://{args['account']}.snowflakecomputing.com:443{url}"

    with requests.sessions.Session() as session:
        return session.request(
            method='post',
            url=full_url,
            headers=headers,
            data=gzip.compress(json.dumps(body).encode()),
            timeout=auth_instance._socket_timeout,
            verify=True,
            stream=False,
            auth=SnowflakeAuth(None),
        )
