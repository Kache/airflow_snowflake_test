"""Workaround for: https://github.com/apache/airflow/issues/34109

DagRunNote has a foreign key `user_id` (and thus a dependency) to User, but it
seems `airflow.models.dagrun` gets loaded first (at least when running `airflow
tasks test DAG_ID TASK_ID`). Loading User first seems to solve the issue.
"""

from airflow.auth.managers.fab.models import User  # noqa
from airflow.models.dagrun import DagRunNote  # noqa
