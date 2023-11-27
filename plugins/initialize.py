import os
import json
import logging

import conn.snowflake

logging.getLogger('snowflake').setLevel(logging.DEBUG)

logging.getLogger('airflow.providers.snowflake.hooks.snowflake.SnowflakeHook').setLevel(logging.DEBUG)

os.environ['AIRFLOW_CONN_SNOWFLAKE'] = json.dumps(conn.snowflake.info)
