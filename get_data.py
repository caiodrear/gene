# imports----------------------------------------------------------------------
import requests
import pandas as pd
# import numpy as np
from tqdm import tqdm


# download data----------------------------------------------------------------


def download_data():

    headers = {'Accept': 'application/json'}
    static_url = 'https://fantasy.premierleague.com/api/bootstrap-static/'

    resp_static = requests.get(static_url, headers=headers).json()

    element_type_names = {
        element_type['id']: element_type['singular_name_short']
        for element_type in resp_static['element_types']}

    player_positions = pd.DataFrame.from_dict({
        player['id']: element_type_names[player['element_type']]
        for player in resp_static['elements']},
        orient='index', columns=['position']).reset_index(names=['element'])

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

    data = data[data['minutes'] > 0]  # only players that have played

    data = data.dropna(subset=['team_h_score']).merge(  # drop unplayed matches
        player_positions, on='element').sort_values(
        ['element', 'kickoff_time'])

    data['time_diffs'] = (
        data.groupby('element')['kickoff_time'].diff().dt.total_seconds()/3600
        ).fillna(0)

    data.to_csv('data/data.csv', index=False)


# test-train split-------------------------------------------------------------
# window_size = 3

# cutoff = 30

# train_data = data[data['round'] < cutoff].drop('round', axis=1)
# test_data = data[data['round'] >= cutoff].drop('round', axis=1)

# def get_window_arrays(data):

#     X, y = [], []
#     for player in tqdm(data['element'].unique(), desc='creating frames'):

#         player_data = data[
#             data['element'] == player].drop('element', axis=1).copy()

#         frame_generator = player_data.drop(
#             player_data.tail(1).index).rolling(window=window_size)

#         for window in frame_generator:

#             if len(window) >= 3:
#                 X.append(np.array(window, float))

#                 points_index = window.index[-1]
#                 y.append(player_data['total_points'].loc[points_index + 1])

#     return np.array(X), np.array(y, float)

# X_train, y_train = get_window_arrays(train_data)
# X_test, y_test = get_window_arrays(test_data)

# np.save('data/X_train', X_train)
# np.save('data/y_train', y_train)
# np.save('data/X_test', X_test)
# np.save('data/y_test', y_test)
