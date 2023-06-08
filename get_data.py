# imports----------------------------------------------------------------------
import requests
from tqdm import tqdm
import json
# download data----------------------------------------------------------------


def download_data(season='22-23'):
    headers = {'Accept': 'application/json'}

    # metadata for players and teams-------------------------------------------
    static_url = 'https://fantasy.premierleague.com/api/bootstrap-static/'
    resp_static = requests.get(static_url, headers=headers).json()

    with open(f'data/{season}/json/bootstrap-static.json', 'w') as json_file:
        json.dump(resp_static, json_file)
    json_file.close()

    # player performance data--------------------------------------------------
    def player_data(player_id):
        player_url = (
            'https://fantasy.premierleague.com/api/'
            f'element-summary/{player_id}/')

        return requests.get(player_url, headers=headers).json()

    resp_players = [player_data(player['id']) for player in tqdm(
        resp_static['elements'], desc='player data')]

    with open(f'data/{season}/json/players.json', 'w') as json_file:
        json.dump(resp_players, json_file)
    json_file.close()

    # fixtures data------------------------------------------------------------
    fixtures_url = 'https://fantasy.premierleague.com/api/fixtures/'

    resp_fixtures = requests.get(fixtures_url, headers=headers).json()

    with open(f'data/{season}/json/fixtures.json', 'w') as json_file:
        json.dump(resp_fixtures, json_file)
    json_file.close()
