from airflow import DAG
import pendulum
from airflow.providers.common.sql.operators.sql import SQLExecuteQueryOperator


with DAG(
    dag_id="snowflake_test_dag",
    start_date=pendulum.datetime(2023, 1, 1, tz='America/Los_Angeles'),
    schedule_interval="* * * * *",
    is_paused_upon_creation=False,
) as dag:
    snowflake = SQLExecuteQueryOperator(
        task_id="query_task",
        conn_id="snowflake",
        sql="SELECT 1, 'a'",
    )
