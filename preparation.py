# imports----------------------------------------------------------------------
import pandas as pd
import numpy as np
from tqdm.notebook import tqdm

# add team performance---------------------------------------------------------


def add_team_performance(data, window_size=38):

    x_home_goals = data[data['was_home']].groupby(
        ['fixture', 'team_h'], as_index=False)[['expected_goals']].sum()
    x_away_goals = data[~data['was_home']].groupby(
        ['fixture', 'team_a'], as_index=False)[['expected_goals']].sum()

    xG_table = x_away_goals.merge(
        x_home_goals, on='fixture', suffixes=['_a', '_h'])

    x_home_goals = xG_table[[
        'fixture', 'team_h', 'expected_goals_h', 'expected_goals_a']].rename(
        columns={
            'team_h': 'team',
            'expected_goals_h': 'xG', 'expected_goals_a': 'xGA'})

    x_away_goals = xG_table[[
        'fixture', 'team_a', 'expected_goals_a', 'expected_goals_h']].rename(
            columns={
                'team_a': 'team',
                'expected_goals_a': 'xG', 'expected_goals_h': 'xGA'})

    xG_table = pd.concat([x_home_goals, x_away_goals])

    xG_cumulative = xG_table.groupby(['team', 'fixture']).sum().groupby(
        level=0).rolling(window_size, min_periods=1).mean(
        ).droplevel(0).reset_index()

    xG_cumulative = xG_cumulative[['fixture']].join(
        xG_cumulative.sort_values('fixture').groupby(
            'team').shift(1)[['xG', 'xGA']]).dropna(how='any')

    return data.merge(xG_cumulative.drop_duplicates('fixture').merge(
        xG_cumulative.drop_duplicates('fixture', keep='last'),
        on='fixture', suffixes=['_h', '_a']), on='fixture')

# data windowing---------------------------------------------------------------


def get_window_arrays(data, window_size=3):

    batches = []
    for player in tqdm(data['element'].unique(), desc='creating frames'):

        player_data = data[
            data['element'] == player].drop('element', axis=1).reset_index(
            drop=True).copy()

        frame_generator = player_data.drop(
            player_data.tail(1).index).rolling(window=window_size)

        for window in frame_generator:

            if len(window) >= window_size:

                points_index = window.index[-1]

                match_data = np.array(player_data[[
                    'was_home', 'team_a_difficulty',
                    'team_h_difficulty', 'time_diffs']].loc[points_index + 1])

                target_data = player_data['total_points'].loc[points_index + 1]

                batch = {
                    'player_data': np.array(window, float),
                    'match_data': match_data,
                    'target_data': target_data}

                batches.append(batch)

    return batches
