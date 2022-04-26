#! /usr/bin/env python

import json
from pathlib import Path
import click

from nba_api.stats.static import teams
from nba_api.stats.endpoints import teamgamelog

@click.command()
@click.option(
    "--incl_path", 
    type=click.Path(file_okay=False,
                    writable=True,
                    # to support the '/' operator below
                    path_type=Path),
    required=True,
    help="Path to store result of NBA API call in all_game_ids.json."
)
def get_game_ids(incl_path):
    """
    call nba api for raptor's season team log
    for each game_id not in our game_id table 
        (implies db conn? can I check a static json?
            where would the json come from, end of our dag?),
    make an additional call for that game_id's boxscore
    serialize each game's boxscore as json for preprocess
    """
    # call team log
    team_list = teams.get_teams()
    raps = [team for team in team_list if team['city'] == 'Toronto'][0]
    team_log = teamgamelog.TeamGameLog(team_id=raps['id'],
                                        season='2021-22')
    # .get_json() returns a json string
    # which is deserialized with .loads(), s for string
    team_log_json = json.loads(team_log.get_json())

    team_log_path = incl_path / "team_game_log.json"
    with open(team_log_path, mode='w') as j:
        json.dump(team_log_json, j)

if __name__ == "__main__":
    get_game_ids()