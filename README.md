Snowflake query operator hangs indefinitely when executed locally

Running a docker compose cluster locally seems fine though. A minimal repro:

```sh
# basic setup
python -m venv .venv
. .venv/bin/activate
pip install "apache-airflow[snowflake] == 2.7.3"

# for creds & AIRFLOW_HOME
cp template.env .env

# see Makefile
make airflow.db
```

There is only one DAG with one query task:

```sh
❯ airflow dags list
dag_id             | filepath              | owner   | paused
===================+=======================+=========+=======
snowflake_test_dag | snowflake_test_dag.py | airflow | None

❯ airflow tasks list snowflake_test_dag
query_task
```

these all succeed as expected:

```
scripts/xenv .env python scripts/test_snowflake_connector.py
scripts/xenv .env airflow tasks test snowflake_test_dag query_task
scripts/xenv .env airflow dags test snowflake_test_dag
```

However, when running a local server, the task hangs with 100% CPU (the DAG is
not paused at creation):

```sh
scripts/xenv .env airflow standalone  # or just scheduler
```

<details>
<summary>proc tree via btop</summary>

    ╭─┐¹cpu┌──┐menu┌┐preset *┌───────────────────────────────┐14:01:28┌───────────────────┐BAT■ 100% ■■■■■■■■■■ ┌┐- 2000ms +┌─╮
    │                                                                                                                         │
    │                                                                                ╭─┐Apple M1 Max┌────────────────────────╮│
    │                                                                              ⢀ │CPU ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■  48%││
    │                                                                 ⡇⡆⡆⡇⡆⣄⣄⣴⣄⣀⣠⣠⢰⣸⢸│C0  ⣶⣶⣶⣶⣶⣶⣶⣶⣴⣶  72%│C5  ⣀⣀⣀⣀⣀⣀⣀⣀⣠⣠  34%││
    │                                                                ⢸⣷⣷⣧⣷⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿│C1  ⣶⣶⣶⣶⣶⣶⣶⣶⣶⣶  72%│C6  ⣤⣤⣴⣴⣦⣤⣤⣴⣶⣦  54%││
    │                                                                ⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿│C2  ⣶⣶⣶⣶⣶⣶⣶⣶⣴⣴  67%│C7  ⣄⣄⣤⣄⣀⣠⣀⣠⣤⣤  37%││
    │                                                                ⢿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿│C3  ⣤⣤⣤⣤⣤⣤⣤⣤⣤⣤  52%│C8  ⣀⣀⣠⣀⣀⣀⣀⣀⣠⣀  28%││
    │                                                                ⠘⡟⡟⡏⡟⡿⡿⡿⣿⣿⣿⣿⢿⢿⢿⢿⡿C4  ⣄⣄⣤⣄⣀⣠⣠⣠⣠⣠  40%│C9  ⣀⣀⣀⣀⣀⣀⣀⣀⣠⢀  26%││
    │                                                                 ⠃⠃⠃⠃⠁⠁⠁⠈  ⠈ ⠈⠸⠘⠁⠇                   LAV: 7.77 6.06 4.74││
    │                                                                                  ──────────────────────────────────────╯│
    │ up 5d 00:20                                                                                                             │
    ╰─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
    ╭─┐⁴proc┌┐f airflow del┌────────────────────────────────────────────────────────┐per-core┌┐reverse┌┐tree┌┐< cpu direct >┌─╮
    │Tree:                                                                              Threads: User:       MemB       Cpu%  │
    │[-]─77168 bash (bash scripts/xenv .env airflow standalone)                                1 myusername  3.2M ⣀⣀⣀⣀⣀  0.0  │
    │ │ [-]─77169 python3.11 (/Users/myusername/Code/airflow_snowflake_test/.venv/bin/pyth)    5 myusername  158M ⣀⣀⣀⢀⢀  0.1  │
    │ │  │ [-]─77171 python3.11 (/Users/myusername/Code/airflow_snowflake_test/.venv/bin/p)    4 myusername  147M ⣀⣀⣀⣀⣀  0.5  │
    │ │  │  │ [-]─77175 python3.11 (gunicorn: master [gunicorn])                               2 myusername   66M ⣀⣀⣀⣀⣀  0.0  │
    │ │  │  │  │  ├─ 77177 python3.11 (gunicorn: worker [gunicorn])                            1 myusername   15M ⣀⣀⣀⣀⣀  0.0  │
    │ │  │  │  │  └─ 77176 python3.11 (gunicorn: worker [gunicorn])                            1 myusername   15M ⣀⣀⣀⣀⣀  0.0  │
    │ │  │  │  └─ 77174 python3.11 (/Users/myusername/Code/airflow_snowflake_test/.venv/bi)    1 myusername   13M ⣀⣀⣀⣀⣀  0.0  │
    │ │  │ [-]─77172 python3.11 (/Users/myusername/Code/airflow_snowflake_test/.venv/bin/p)    1 myusername  126M ⣀⣀⣀⣀⣀  0.0  │
    │ │  │  │ [-]─77173 python3.11 (gunicorn: master [airflow-webserver])                      2 myusername  176M ⣀⣀⣀⢀⢀  1.7  │
    │ │  │  │  │  ├─ 78489 python3.11 ([ready] gunicorn: worker [airflow-webserver])           1 myusername   28M ⣀⣀⣀⣀⣀  0.0  │
    │ │  │  │  │  ├─ 78488 python3.11 ([ready] gunicorn: worker [airflow-webserver])           1 myusername   28M ⣀⣀⣀⣀⣀  0.0  │
    │ │  │  │  │  ├─ 78487 python3.11 ([ready] gunicorn: worker [airflow-webserver])           1 myusername   29M ⣀⣀⣀⣀⣀  0.0  │
    │ │  │  │  │  └─ 78486 python3.11 ([ready] gunicorn: worker [airflow-webserver])           1 myusername   28M ⣀⣀⣀⣀⣀  0.0  │
    │ │  │ [-]─77170 python3.11 (/Users/myusername/Code/airflow_snowflake_test/.venv/bin/p)    2 myusername  149M ⣀⣀⣀⣀⣀  0.0  │
    │ │  │  │ [-]─77195 python3.11 (/Users/myusername/Code/airflow_snowflake_test/.venv/bi)    2 myusername  133M ⣀⣀⣀⣀⡀  0.0  │
    │ │  │  │  │  └─ 77198 python3.11 (airflow task runner: snowflake_test_dag query_task )    1 myusername   96M ⣀⣀⣀⣿⣿  100  │
    │ │  │  │ [-]─77188 python3.11 (gunicorn: master [gunicorn])                               2 myusername   67M ⣀⣀⣀⣀⣀  0.0  │
    │ │  │  │  │  ├─ 77191 python3.11 (gunicorn: worker [gunicorn])                            1 myusername   16M ⣀⣀⣀⣀⣀  0.0  │
    │ │  │  │  │  └─ 77190 python3.11 (gunicorn: worker [gunicorn])                            1 myusername   15M ⣀⣀⣀⣀⣀  0.0  │
    │ │  │  │  ├─ 77189 python3.11 (airflow scheduler -- DagFileProcessorManager)              2 myusername  101M ⣀⣀⣀⣀⣀  0.0  │
    │ │  │  │  └─ 77187 python3.11 (/Users/myusername/Code/airflow_snowflake_test/.venv/bi)    1 myusername   14M ⣀⣀⣀⣀⣀  0.0  │
    │                                                                                                                         │
    ╰┘↑ select ↓└┘info ↵└┘terminate└┘kill└┘signals└────────────────────────────────────────────────────────────────────┘16/21└╯

</details>


More context:

```sh
❯ uname -a
Darwin Kache-J6J9FXYF3L 22.6.0 Darwin Kernel Version 22.6.0: Wed Jul  5 22:22:05 PDT 2023; root:xnu-8796.141.3~6/RELEASE_ARM64_T6000 arm64
```

Logs from the run are included in this repo. A second commit shows the lines added after SIGINT the hanging task.
