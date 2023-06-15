
# train-validate-test split----------------------------------------------------














# class GeneData:
#     def __init__(self, data):

#         self.data = data

#     def prepare(
#             self, fixture_window_size, position,
#             player_window_size, ttv_split=[0.7,0.2,0.1]):

#         self.add_team_performance(window_size=fixture_window_size)

#         self.ttv_split(splits=ttv_split)

#         self.

#         self.

#     # add xG and xGA for teams from recent games-------------------------------
#     def add_team_performance(self, window_size=38):

#         x_home_goals = self.data[self.data['was_home']].groupby(
#             ['fixture', 'team_h'], as_index=False)[['expected_goals']].sum()
#         x_away_goals = self.data[~self.data['was_home']].groupby(
#             ['fixture', 'team_a'], as_index=False)[['expected_goals']].sum()

#         xG_table = x_away_goals.merge(
#             x_home_goals, on='fixture', suffixes=['_a', '_h'])

#         x_home_goals = xG_table[[
#             'fixture', 'team_h',
#             'expected_goals_h', 'expected_goals_a']].rename(
#             columns={
#                 'team_h': 'team',
#                 'expected_goals_h': 'xG', 'expected_goals_a': 'xGA'})

#         x_away_goals = xG_table[[
#             'fixture', 'team_a',
#             'expected_goals_a', 'expected_goals_h']].rename(
#                 columns={
#                     'team_a': 'team',
#                     'expected_goals_a': 'xG', 'expected_goals_h': 'xGA'})

#         xG_table = pd.concat([x_home_goals, x_away_goals])

#         xG_cumulative = xG_table.groupby(['team', 'fixture']).sum().groupby(
#             level=0).rolling(window_size, min_periods=1).mean(
#             ).droplevel(0).reset_index()

#         xG_cumulative = xG_cumulative[['fixture']].join(
#             xG_cumulative.sort_values('fixture').groupby(
#                 'team').shift(1)[['xG', 'xGA']]).dropna(how='any')

#         self.data = self.data.merge(xG_cumulative.drop_duplicates(
#             'fixture').merge(xG_cumulative.drop_duplicates(
#                 'fixture', keep='last'),
#             on='fixture', suffixes=['_h', '_a']), on='fixture')

#     # add xG and xGA for teams from recent games-------------------------------
#     window_size = 3

#     def get_window_arrays(self, window_size=3):

#         X, y = [], []
#         for player in tqdm(data['element'].unique(), desc='creating frames'):

#             player_data = data[
#                 data['element'] == player].drop('element', axis=1).reset_index(
#                 drop=True).copy()

#             frame_generator = player_data.drop(
#                 player_data.tail(1).index).rolling(window=window_size)

#             for window in frame_generator:

#                 if len(window) >= window_size:
#                     X.append(np.array(window, float))

#                     points_index = window.index[-1]

#                     y.append(player_data['total_points'].loc[points_index + 1])

#         return np.array(X), np.array(y, float)

#     X_train, y_train = get_window_arrays(train_data)
#     X_test, y_test = get_window_arrays(test_data)