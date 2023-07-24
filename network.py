# imports----------------------------------------------------------------------
from keras.models import Model
from keras.layers import (
    Input, Conv1D, MaxPooling1D, Flatten, Dense, Dropout, concatenate)


class GeneModel:
    def __init__(self, gene_data):

        self.gene_data = gene_data

        # match data model-----------------------------------------------------
        tab_input = Input(shape=(gene_data.train_data['match_data'].shape[1],))

        dense_1 = Dense(8, activation="relu")(tab_input)
        dense_2 = Dense(32, activation="relu")(dense_1)
        dense_3 = Dense(16, activation="relu")(dense_2)
        dense_4 = Dense(4, activation="relu")(dense_3)

        tab_output = dense_4

        # player data model----------------------------------------------------
        win_input = Input(shape=gene_data.train_data['player_data'].shape[1:3])

        conv_1 = Conv1D(
            filters=128, kernel_size=2, activation='relu')(win_input)
        pool_1 = MaxPooling1D(pool_size=4)(conv_1)

        dense = Dense(64, activation="relu")(pool_1)

        # dropout = Dropout(0.0001)(pool_1)

        # conv_2 = Conv1D(
        #     filters=16, kernel_size=1, activation='relu')(dropout)
        # pool_2 = MaxPooling1D(pool_size=1)(conv_2)

        # flat = Flatten()(conv_1)
        # dense = Dense(10, activation='relu')(flat)

        win_output = dense

        # model compilation----------------------------------------------------

        # concat = concatenate(
        #     [tab_output, win_output], name='concatenated_layer')

        output = Dense(
            1, activation='linear', name='output_layer')(win_output)

        inputs = [tab_input, win_input]

        model = Model(inputs=[win_input], outputs=[output])
        model.compile(
            loss='mse', optimizer='adam',
            )

        self.model = model

    def train(self, epochs, batch_size, verbose=0):

        train_data = [
            self.gene_data.train_data['match_data'],
            self.gene_data.train_data['player_data']]

        train_data = self.gene_data.train_data['player_data']

        validation_data = ([
            self.gene_data.validation_data['match_data'],
            self.gene_data.validation_data['player_data']],
                self.gene_data.validation_data['target_data'])

        validation_data = ([
            self.gene_data.validation_data['player_data']],
                self.gene_data.validation_data['target_data'])

        self.model.fit(
            train_data, self.gene_data.train_data['target_data'],
            validation_data=validation_data,
            epochs=epochs, batch_size=batch_size, verbose=verbose)
