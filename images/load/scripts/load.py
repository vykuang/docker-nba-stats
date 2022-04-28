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
    help="Path which contains 'nba_stats_populate.sql."
)
@click.option(
    "--incl_path", 
    type=click.Path(file_okay=False,
                    writable=True,
                    # to support the '/' operator below
                    path_type=Path),
    required=True,
    help="Path which contains 'trad_boxscores.json'."
)
@click.option(
    "--conn_str", 
    type=click.STRING,
    help="Connection string to the postgres database. Must contain dbname,\
    host, user, and password",
)
def populate_boxscore_table(sql_path, incl_path, conn_str=None):
    """
    UPSERTing all records into the table
    Postgres does not have native UPSERT like MySQL,
    but it does have INSERT ... ON CONFLICT (conflict-target) DO UPDATE
    or in our case DO NOTHING
    where conflict-target is the (game_id, player_id) that we've set
    as unique when creating this table
    Even though we eliminated logged games when checking for past game_IDs,
    this helps ensure IDEMPOTENCY

    Use psycopg2.extras.execute_batch or execute_values
    for performance gain over executemany, which is just 
    looped .execute()
    """
    import json
    import psycopg2
    # explicitly required for execute_batch
    import psycopg2.extras

    with open(incl_path / 'trad_boxscores.json') as j, \
         open(sql_path / 'nba_stats_create.sql') as sql_create, \
         open(sql_path / 'nba_stats_populate.sql') as sql_upsert:
        trad_box = json.load(j)
        create_table =  sql_create.read()
        populate = sql_upsert.read()

    if not conn_str:
        conn_str = "dbname='nba_stats' \
            host='nba-stats-db' \
            port='5432' \
            user='nba_stats' \
            password='secret'"
    
    conn = None
    try:
        conn = psycopg2.connect(conn_str)

        with conn:
            with conn.cursor() as curs:
                curs.execute(create_table)
                psycopg2.extras.execute_batch(curs, populate, trad_box['trad_box'])
            conn.commit()
            res = 0
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
        res = 1
    finally:
        if conn is not None:
            conn.close()
        return res

if __name__ == "__main__":
    populate_boxscore_table()