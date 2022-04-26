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
}

@dag(
    # function name now acts as dag_id
    default_args=default_args,    
    description="Fetches boxscores from nba.com via nba_api using Docker",
    schedule_interval=timedelta(days=1),
    catchup=False
    )
def extract_nba_boxscore():
    """doc string here"""
    team_logs = DockerOperator(
        task_id="get_team_logs",
        image="nba-stats/nba-api-fetch",
        command=[
            "get-game-ids",
            "--incl_path",
            "/data"
        ],
        # attaches the container to airflow's container so API call can reach
        network_mode="airflow",
        mount_tmp_dir=False,
        mounts=[
            Mount(source="/tmp/nba_stats/data", target="/data", type='bind')
        ],
        auto_remove=True,   # auto-removal of container when process exits
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
        mount_tmp_dir=False,
        # originally volume in book; API changed in v2.4.0
        mounts=[
            Mount(source="/tmp/nba_stats/data", target="/data", type='bind')
        ],
        auto_remove=True,
        # docker_url="unix://var/run/docker.sock"
    )

    # TASK DEPENDENCY #
    team_logs >> new_game_ids

nba_boxscore_dag = extract_nba_boxscore()