# imports----------------------------------------------------------------------
import pandas as pd
import numpy as np
import random
from sklearn.preprocessing import MinMaxScaler
from tqdm.notebook import tqdm

# gene class-------------------------------------------------------------------


class GeneData:
    def __init__(self, data):
        self.raw_data = data
        self.data = data

    def reset_data(self):
        self.data = self.raw_data

    # add team performance-----------------------------------------------------
    def add_team_performance(self, window_size=38):

        x_home_goals = self.data[self.data['was_home']].groupby(
            ['fixture', 'team_h'], as_index=False)[['expected_goals']].sum()
        x_away_goals = self.data[~self.data['was_home']].groupby(
            ['fixture', 'team_a'], as_index=False)[['expected_goals']].sum()

        xG_table = x_away_goals.merge(
            x_home_goals, on='fixture', suffixes=['_a', '_h'])

        x_home_goals = xG_table[[
            'fixture', 'team_h', 'expected_goals_h', 'expected_goals_a'
            ]].rename(columns={
                'team_h': 'team', 'expected_goals_h': 'xG',
                'expected_goals_a': 'xGA'})

        x_away_goals = xG_table[[
            'fixture', 'team_a', 'expected_goals_a', 'expected_goals_h'
            ]].rename(columns={
                'team_a': 'team',
                'expected_goals_a': 'xG', 'expected_goals_h': 'xGA'})

        xG_table = pd.concat([x_home_goals, x_away_goals])

        xG_cumulative = xG_table.groupby(['team', 'fixture']).sum().groupby(
            level=0).rolling(window_size, min_periods=1).mean(
            ).droplevel(0).reset_index()

        xG_cumulative = xG_cumulative[['fixture']].join(
            xG_cumulative.sort_values('fixture').groupby(
                'team').shift(1)[['xG', 'xGA']]).dropna(how='any')

        self.data = self.data.merge(xG_cumulative.drop_duplicates(
            'fixture').merge(xG_cumulative.drop_duplicates(
                'fixture', keep='last'),
                on='fixture', suffixes=['_h', '_a']), on='fixture')

    # filter data for player positions----------------------------------------
    def position_filter(self, position):

        self.position = position

        self.data = self.data[(
            self.data['position'] == 'MID')].drop('position', axis=1)

        self.data.drop([
            'fixture', 'opponent_team', 'kickoff_time', 'round',
            'player_name_short', 'player_name_full', 'team_h', 'team_a',
            'team_h_name', 'team_a_name', 'player_team'], axis=1, inplace=True)

    # data windowing and train, test, valdiation splitting---------------------
    def window_split(self, window_size=3, tvt_size=[0.7, 0.2, 0.1]):

        windows = [[
            player_indices[n:n + window_size], player_indices[n + window_size]]
            for player_indices in [
                self.data[self.data['element'] == player].index
                for player in self.data['element'].unique()]
            for n in range(len(player_indices) - window_size)]

        random.shuffle(windows)

        tvt_size = np.floor(np.cumsum(
            np.array(tvt_size) * len(windows))).astype('int')

        self.train_indices = windows[:tvt_size[0]]
        self.validation_indices = windows[tvt_size[0]:tvt_size[1]]
        self.test_indices = windows[tvt_size[1]:]

    # data scaling-------------------------------------------------------------
    def scale_data(self):

        train_data = self.data.loc[list(set(
            index for window in self.train_indices for index in window[0]))]

        no_scaling = [
            'was_home', 'clean_sheets', 'yellow_cards', 'red_cards', 'starts']

        min_max_vars = [
            'time_diffs', 'minutes', 'bonus', 'goals_conceded', 'own_goals',
            'bps', 'influence', 'creativity', 'threat', 'ict_index', 'value',
            'transfers_balance', 'selected', 'transfers_in', 'transfers_out',
            'expected_goals_conceded', 'total_points', 'team_a_difficulty',
            'team_h_difficulty', 'xG_h', 'xGA_h', 'xG_a', 'xGA_a']

        if self.position == 'GKP':
            player_metrics = ['penalties_saved', 'saves']
        else:
            player_metrics = [
                'penalties_missed', 'goals_scored', 'expected_goals',
                'assists', 'expected_assists', 'expected_goal_involvements']

        scaler = MinMaxScaler().set_output(transform='pandas')
        scaler.fit(train_data[min_max_vars + player_metrics])

        self.data = self.data[no_scaling].join(
            scaler.transform(self.data[min_max_vars + player_metrics]))

    # data wrangling-----------------------------------------------------------
    def wrangle_data(self):

        def get_batches(data_indices):

            batches = {'player_data': [], 'match_data': [], 'target_data': []}

            for window_indices in tqdm(data_indices):

                batches['player_data'].append(
                    np.array(self.data.loc[window_indices[0]], float))

                batches['match_data'].append(np.array(self.data[[
                    'was_home', 'team_a_difficulty', 'team_h_difficulty',
                    'time_diffs']].loc[window_indices[1]], float))

                batches['target_data'].append(
                    np.array(self.data['total_points'].loc[window_indices[1]]))

            for component in batches:
                batches[component] = np.array(batches[component])

            return batches

        self.train_data = get_batches(self.train_indices)
        self.validation_data = get_batches(self.validation_indices)
        self.test_data = get_batches(self.test_indices)
