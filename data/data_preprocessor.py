import pandas as pd
from sklearn.preprocessing import MinMaxScaler

class DataPreprocessor:
    def __init__(self):
        self.scaler = MinMaxScaler()

    def preprocess(self, data):
        """
        Preprocess raw market data.
        """
        # Drop missing values
        data = data.dropna()

        # Normalize features
        scaled_data = self.scaler.fit_transform(data)

        # Create features and target
        X = scaled_data[:, :-1]
        y = scaled_data[:, -1]

        return X, y