.PHONY: script
script:
	scripts/xenv .env python scripts/test_snowflake_connector.py

.PHONY: task
task: airflow.db
	scripts/xenv .env airflow tasks test snowflake_test_dag query_task

.PHONY: dag
dag: airflow.db
	scripts/xenv .env airflow dags test snowflake_test_dag

.PHONY: dag
standalone: airflow.db
	scripts/xenv .env airflow standalone

.PHONY: clean
clean:
	rm -rf airflow.db logs standalone_admin_password.txt

.PHONY: clean-all
clean-all: clean
	rm -rf .venv

airflow.db:
	scripts/xenv .env airflow db migrate
	scripts/xenv .env airflow users create --role Admin --username admin --password admin --email admin --firstname Local --lastname Test
