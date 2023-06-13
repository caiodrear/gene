# imports----------------------------------------------------------------------
import requests
from tqdm import tqdm
import json

import pandas as pd

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

        return requests.get(player_url, headers=headers).json()['history']

    resp_players = [
        gameweek_data for player in tqdm(
            resp_static['elements'], desc='player data')
        for gameweek_data in player_data(player['id'])]

    with open(f'data/{season}/json/players.json', 'w') as json_file:
        json.dump(resp_players, json_file)
    json_file.close()

    # fixtures data------------------------------------------------------------
    fixtures_url = 'https://fantasy.premierleague.com/api/fixtures/'

    resp_fixtures = requests.get(fixtures_url, headers=headers).json()

    with open(f'data/{season}/json/fixtures.json', 'w') as json_file:
        json.dump(resp_fixtures, json_file)
    json_file.close()


# process data-----------------------------------------------------------------


def process_data(season='22-23'):
    # merge player performance and metadata------------------------------------

    with open(f'data/{season}/json/bootstrap-static.json', 'r') as json_file:
        data_static = json.load(json_file)
    json_file.close()

    with open(f'data/{season}/json/players.json', 'r') as json_file:
        data = pd.DataFrame(json.load(json_file))
    json_file.close()

    postion_names = {
        element_type['id']: element_type['singular_name_short']
        for element_type in data_static['element_types']}

    player_meta = pd.DataFrame.from_dict({
        player['id']: [
            postion_names[player['element_type']], player['web_name'],
            player['first_name'] + ' ' + player['second_name']]
        for player in data_static['elements']}, orient='index',
        columns=[
            'position', 'player_name_short',
            'player_name_full']).reset_index(names=['element'])

    data = data.merge(player_meta, on='element')

    # add fixture ratings and team data----------------------------------------

    with open(f'data/{season}/json/fixtures.json', 'r') as json_file:
        data_fixtures = json.load(json_file)
    json_file.close()

    fixture_ratings = pd.DataFrame(
        data_fixtures).rename(columns={'id': 'fixture'})[[
            'fixture', 'team_h', 'team_a',
            'team_h_difficulty', 'team_a_difficulty']]

    data = data.merge(fixture_ratings, on='fixture')

    # add team metadata--------------------------------------------------------

    team_names = pd.DataFrame(data_static['teams'])[
        ['id', 'name']].set_index('id')

    data = data.join(
        team_names, on='team_h').rename(
        columns={'name': 'team_h_name'}).join(
        team_names, on='team_a',).rename(
        columns={'name': 'team_a_name'})

    data['player_team'] = (
        data['was_home'] * data['team_h'] +
        (1-data['was_home']) * data['team_a'])

    # add time features--------------------------------------------------------

    data['kickoff_time'] = pd.to_datetime(data['kickoff_time'])

    data = data.sort_values(
        ['element', 'kickoff_time'])

    data['time_diffs'] = (
        data[data['minutes'] > 0].groupby('element')['kickoff_time'].diff(
        ).dt.total_seconds()/3600).fillna(0)

    # save data----------------------------------------------------------------

    data.to_csv(f'data/{season}/player_data.csv', index=False)

    return data
