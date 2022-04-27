#! /usr/bin/env python

import json
from pathlib import Path
import click
import time
import random

from nba_api.stats.endpoints import boxscoretraditionalv2 as boxv2

@click.command()
@click.option(
    "--resp_path", 
    type=click.Path(file_okay=False,
                    writable=True,
                    # to support the '/' operator below
                    path_type=Path),
    required=True,
    help="Path to store results of stats.NBA API call for each game's boxscore as <game_id>.json."
)
@click.option(
    "--incl_path", 
    type=click.Path(file_okay=False,
                    writable=True,
                    # to support the '/' operator below
                    path_type=Path),
    required=True,
    help="Path which contains 'game_ids_new.json'."
)
def get_boxscore(resp_path, incl_path):
    """
    call nba api for game boxscore for each game_id?
    maybe score in json/dict - game_id: boxscore
    """

    game_ids_fp = incl_path / 'game_ids_new.json'
    if not game_ids_fp.exists():
        raise FileNotFoundError
    with open(game_ids_fp) as js_read:
        game_ids = json.load(js_read)

    for game_id in game_ids['Game_IDs']:
        try:
            boxscore_call = boxv2.BoxScoreTraditionalV2(game_id=game_id).get_json()
            boxscore_loads = json.loads(boxscore_call)
        except json.decoder.JSONDecodeError as msg:
            raise msg
        
        with open(resp_path / f"{game_id}.json", mode='w') as js_write:
            json.dump(boxscore_loads, js_write)
        #  delay to avoid hammering the requests
        wait = random.gammavariate(alpha=9, beta=0.4)
        time.sleep(wait)

if __name__ == "__main__":
    get_boxscore()