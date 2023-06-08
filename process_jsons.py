# imports----------------------------------------------------------------------
import requests
import pandas as pd
from tqdm import tqdm
# download data----------------------------------------------------------------


def download_data():
    # get all player id and postions-------------------------------------------

    headers = {'Accept': 'application/json'}
    static_url = 'https://fantasy.premierleague.com/api/bootstrap-static/'

    resp_static = requests.get(static_url, headers=headers).json()

    element_type_names = {
        element_type['id']: element_type['singular_name_short']
        for element_type in resp_static['element_types']}

    player_positions = pd.DataFrame.from_dict({
        player['id']: [
            element_type_names[player['element_type']], player['web_name'],
            player['first_name'] + ' ' + player['second_name']]
        for player in resp_static['elements']}, orient='index',
        columns=[
            'position', 'player_name_short',
            'player_name_full']).reset_index(names=['element'])

    # collect match data for each player---------------------------------------

    data = []
    for player in tqdm(resp_static['elements'], desc='downloading data'):

        player_id = player['id']
        player_url = (
            'https://fantasy.premierleague.com/api/'
            f'element-summary/{player_id}/')

        resp_player = requests.get(player_url, headers=headers).json()

        data += resp_player['history']

    data = pd.DataFrame(data)
    data['kickoff_time'] = pd.to_datetime(data['kickoff_time'])

    # add days since player last played and player positions and teams---------

    data = data.sort_values(
        ['element', 'kickoff_time']).sort_values('kickoff_time')

    data = data.merge(player_positions, on='element')

    data['player_team'] =  data['team_h'] * data['was_home'] + 

    data['time_diffs'] = (
        data[data['minutes'] > 0].groupby('element')['kickoff_time'].diff(
        ).dt.total_seconds()/3600).fillna(0)

    # add team difficulty ratings and names to fixtures------------------------

    fixtures_url = 'https://fantasy.premierleague.com/api/fixtures/'

    fixtures_resp = requests.get(fixtures_url, headers=headers).json()

    fixture_ratings = pd.DataFrame(
        fixtures_resp).rename(columns={'id': 'fixture'})[[
            'fixture', 'team_h', 'team_a',
            'team_h_difficulty', 'team_a_difficulty']]

    team_names = pd.DataFrame(
        resp_static['teams']).rename(
        columns={'id': 'team_h', 'name': 'team_h_name'})[[
            'team_h', 'team_h_name']]

    fixture_ratings = fixture_ratings.merge(team_names, on='team_h')

    team_names = team_names.rename(
        columns={'team_h': 'team_a', 'team_h_name': 'team_a_name'})

    fixture_ratings = fixture_ratings.merge(team_names, on='team_a')

    data = data.merge(fixture_ratings, on='fixture')

    # data.to_csv('data/data.csv', index=False)

    return data
