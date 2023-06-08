
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
