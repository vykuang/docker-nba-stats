#! /usr/bin/env python

import json
from pathlib import Path

import psycopg2
import click

@click.command()
@click.option(
    "--sql_path", 
    type=click.Path(file_okay=False,
                    writable=True,
                    # to support the '/' operator below
                    path_type=Path),
    required=True,
    help="Path which contains 'nba_stats_sel_game_id.sql."
)
@click.option(
    "--incl_path", 
    type=click.Path(file_okay=False,
                    writable=True,
                    # to support the '/' operator below
                    path_type=Path),
    required=True,
    help="Path to store 'game_ids_logged.json'."
)
@click.option(
    "--conn_str", 
    type=click.STRING,
    help="Connection string to the postgres database."
)
def get_logged_game_ids(sql_path, incl_path, conn_str):
    """
    After populating/updating the table, get the set of logged
    game_ids and output to game_ids_logged.json for next run's
    comparison
    
    Args:
        incl_path: Path object of which folder to output the json log
        conn_str: str object containing the database connection info
    Raises:
        FileNotFoundError if incl_path is invalid
        database connection error if conn_str is invalid
    """
    import psycopg2
    import json
    
    with open(sql_path / 'nba_stats_sel_game_id.sql') as sql:
        query = sql.read()
        
    log_json = {}
    try:
        conn = psycopg2.connect(conn_str)

        with conn:
            with conn.cursor() as curs:                
                curs.execute(query)
                logged_game_ids = curs.fetchall()
                
        # returns as a list of tuple, where each tuple is one record
        # since our record only has one column (game_id), we access
        # via [0] indexing
        log_list = [game_id[0] for game_id in logged_game_ids]
        log_json["Game_IDs"] = log_list
        
    except (psycopg2.OperationalError, psycopg2.ProgrammingError) as error:
        print(error)
        
    finally:
        with open(incl_path / "game_ids_logged.json", mode='w') as j:
            json.dump(log_json, j)
        if conn is not None:
            conn.close()
            
    return logged_game_ids

if __name__ == "__main__":
    get_logged_game_ids()