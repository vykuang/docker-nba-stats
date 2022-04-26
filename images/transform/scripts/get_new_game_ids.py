#! /usr/bin/env python

import json
from pathlib import Path
import click

@click.command()
@click.option(
    "--incl_path", 
    type=click.Path(file_okay=False,
                    writable=True,
                    # to support the '/' operator below
                    path_type=Path),
    required=True,
    help="Path to find all_game_ids.json and game_ids_logged.json."
)
def get_new_game_ids(incl_path):
    """Returns list of game IDs that have not been logged yet
    """
    team_log_path = incl_path / "team_game_log.json"
    try:
        with open(team_log_path, mode='r') as js_read:
            team_log_json = json.load(js_read)
    except FileNotFoundError as e:
        print(e, "team_game_log.json not found")

    num_games = len(team_log_json['resultSets'][0]['rowSet'])

    # i iterates through each game;  [1] selects the game_id from list
    game_ids = [team_log_json['resultSets'][0]['rowSet'][i][1] 
                for i in range(num_games)]

    logged_ids_path = incl_path / 'game_ids_logged.json'
    try:
        with open(logged_ids_path, mode='r') as js_read:
            logged_ids_json = json.load(js_read)

    except FileNotFoundError as e:
        logged_ids_json = {'Game_IDs': []}
        

    logged_ids = set(logged_ids_json['Game_IDs'])
    
    # removes shared IDs between game_ids and logged_ids
    # and assigns to ids_new
    game_ids_new = set(game_ids).difference(logged_ids)
    # SET is not serializable; must convert back to LIST
    game_ids_new_json = {'Game_IDs': list(game_ids_new)}
    
    new_ids_path = incl_path / "game_ids_new.json"
    
    with open(new_ids_path, mode="w") as j:
        json.dump(game_ids_new_json, j)
        
    # return game_ids_new_json

if __name__ == "__main__":
    get_new_game_ids()                            