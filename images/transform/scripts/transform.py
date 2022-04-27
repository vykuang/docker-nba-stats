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
    help="Path to find all <game_id>.json."
)
@click.option(
    "--resp_path", 
    type=click.Path(file_okay=False,
                    writable=True,
                    # to support the '/' operator below
                    path_type=Path),
    required=True,
    help="Path to store boxscore transformation results"
)
def transform_boxscore(incl_path, resp_path):
    """
    Loads the boxscore json responses from 
        resp_path / "<game_id>.json" 
    and transforms to a format convenient for postgresql insertion
    stored as 'trad_boxscores.json' in incl_path
    """
    
    first_read = True
    boxscores = {}
    boxscores['trad_box'] = []

    # game_ids always have 10 digits \d{10}
    # but .glob does not use regex
    # just specify that file name ends with a digit
    boxscore_gen = resp_path.glob(r'*[0123456789].json')

    for game in boxscore_gen:
        with open(game) as js_read:
            boxscore_loads = json.load(js_read)

        boxscore_json = boxscore_loads['resultSets'][0]['rowSet']

        if first_read:
            headers = boxscore_loads['resultSets'][0]['headers']
            # converting the keyword `TO` to avoid conflict
            headers_conv = [header.lower() if header != "TO" else "turnover"
                            for header in headers]
            headers_conv = [header if header != "min" else "minutes"
                            for header in headers_conv]
            boxscores['headers'] = headers_conv
            first_read = False
    
        # appending each player boxscore to overall list
        for player_box in boxscore_json:            
            boxscores['trad_box'].append(player_box)         
        
    # data staging
    with open(incl_path / 'trad_boxscores.json', mode='w') as j:
        json.dump(boxscores, j)

if __name__ == "__main__":
    transform_boxscore()