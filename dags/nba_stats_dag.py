from datetime import datetime, timedelta
from pathlib import Path

from airflow.providers.docker.operators.docker import DockerOperator
from airflow.decorators import dag
from docker.types import Mount

default_args = {
    'owner': 'vk',
    'start_date': datetime(2022, 2, 1),
    # 'retries': 2,
    # 'retry_delay': timedelta(minutes=2)
    'auto_remove': 'True',
    'mount_tmp_dir':'False',
}

CONN_STR = """dbname='nba_stats'
host='nba-stats-db'
port='5433'
user='nba_stats'
password='nba_stats'"""

@dag(
    # function name now acts as dag_id
    default_args=default_args,    
    description="Fetches boxscores from nba.com via nba_api using Docker",
    schedule_interval=timedelta(days=1),
    catchup=False
    )
def nba_boxscore():
    """doc string here"""
    team_logs = DockerOperator(
        task_id="get_team_logs",
        image="nba-stats/extract-nba-api",
        command=[
            "get-game-ids",
            "--incl_path",
            "/data"
        ],
        # attaches the container to airflow's container so API call can reach
        network_mode="nba-stats",
        # mount_tmp_dir=False,
        mounts=[
            Mount(source="data", 
                    target="/data", 
                    type="volume")
        ],
        # auto_remove=True,   # auto-removal of container when process exits
        # this may not be necessary if it's been mounted in docker compose
        # docker_url="unix://var/run/docker.sock"
    )

    new_game_ids = DockerOperator(
        task_id="get_new_ids",
        image="nba-stats/transform",
        command=[
            "get-new-ids",
            "--incl_path",
            "/data",
        ],
        # allows mounts param to be used while running docker-in-docker
        # mount_tmp_dir=False,
        # originally volume in book; API changed in v2.4.0
        mounts=[
            Mount(source="data", 
                    target="/data", 
                    type="volume"),
        ],
        # auto_remove=True,
        # docker_url="unix://var/run/docker.sock"
    )

    get_boxscores = DockerOperator(
        task_id="get_boxscores",
        image="nba-stats/extract-nba-api",
        command=[
            "get-boxscores",
            "--incl_path",
            "/data",
            "--resp_path",
            "/data/resp",
        ],
        # attaches the container to airflow's container so API call can reach
        network_mode="nba-stats",
        # mount_tmp_dir=False,
        mounts=[
            Mount(source="data", 
                    target="/data", 
                    type="volume"),
            # Mount(source="/tmp/nba_stats/data/resp/", 
            #         target="/data/resp/",
            #         type="bind")
        ],
        # auto_remove=True,   # auto-removal of container when process exits
        # this may not be necessary if it's been mounted in docker compose
        # docker_url="unix://var/run/docker.sock"
    )

    transform_box = DockerOperator(
        task_id="transform_box",
        image="nba-stats/transform",
        command=[
            "transform",
            "--incl_path",
            "/data",
            "--resp_path",
            "/data/resp"
        ],
        # allows mounts param to be used while running docker-in-docker
        # mount_tmp_dir=False,
        # originally volume in book; API changed in v2.4.0
        mounts=[
            Mount(source="data", 
                    target="/data", 
                    type="volume"),
        ],
        # auto_remove=True,
        # docker_url="unix://var/run/docker.sock"
    )
    load_box = DockerOperator(
        task_id="load_boxscore",
        image="nba-stats/load",
        command=[
            "load",
            "--sql_path",
            "/sql",
            "--incl_path",
            "/data",
            "--conn_str",
            f"{CONN_STR}",
        ],
        mounts=[
            Mount(source="data", 
                    target="/data", 
                    type="volume"),
        ]
    )
    create_log = DockerOperator(
        task_id="create_log",
        image="nba-stats/load",
        command=[
            "create-log",
            "--sql_path",
            "/sql",
            "--incl_path",
            "/data",
            "--conn_str",
            f"{CONN_STR}",
        ],
        mounts=[
            Mount(source="data", 
                    target="/data", 
                    type="volume"),
        ]
    )

    # TASK DEPENDENCY #
    team_logs >> new_game_ids >> get_boxscores >> transform_box \
        >> load_box >> create_log

nba_boxscore_dag = nba_boxscore()