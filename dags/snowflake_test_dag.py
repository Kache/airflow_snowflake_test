from airflow import DAG
import pendulum
from airflow.providers.common.sql.operators.sql import SQLExecuteQueryOperator
from airflow.operators.python import PythonOperator

import utils
import conn.snowflake


with DAG(
    dag_id="snowflake_test_dag",
    start_date=pendulum.datetime(2023, 1, 1, tz='America/Los_Angeles'),
    schedule_interval="* * * * *",
    is_paused_upon_creation=False,
) as dag:

    # snowflake = SQLExecuteQueryOperator(
    #     task_id="query_task",
    #     conn_id="snowflake",
    #     sql="SELECT 1, 'a'",
    # )

    def auth_snowflake():
        resp = utils.auth_snowflake(conn.snowflake.args)
        if not resp.ok:
            raise RuntimeError("Failed to authenticate with Snowflake")

    PythonOperator(
        task_id="auth_task",
        python_callable=auth_snowflake,
    )
