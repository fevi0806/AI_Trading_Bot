import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Conv1D, MaxPooling1D, Flatten

class PredictiveModel:
    def __init__(self):
        self.model = self.build_model()

    def build_model(self):
        model = Sequential([
            Conv1D(filters=64, kernel_size=3, activation='relu', input_shape=(60, 1)),
            MaxPooling1D(pool_size=2),
            LSTM(50, return_sequences=True),
            LSTM(50),
            Dense(1)
        ])
        model.compile(optimizer='adam', loss='mse')
        return model

    def train(self, X_train, y_train):
        self.model.fit(X_train, y_train, epochs=10, batch_size=32)

    def predict(self, X_test):
        return self.model.predict(X_test)