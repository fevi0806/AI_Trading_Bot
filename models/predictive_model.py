import pandas as pd
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
from sklearn.model_selection import train_test_split
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

class PredictiveModel:
    def __init__(self, tickers, lookback=50, save_path="models/"):
        self.tickers = tickers
        self.lookback = lookback
        self.save_path = save_path
        os.makedirs(self.save_path, exist_ok=True)  # Ensure the directory exists

    def load_data(self, ticker):
        """Loads preprocessed ETF data."""
        file_path = f"data/{ticker}_processed.csv"
        if not os.path.exists(file_path):
            logging.warning(f"Data file not found for {ticker}, skipping...")
            return None
        return pd.read_csv(file_path, index_col=0)

    def prepare_data(self, df):
        """Creates time-series data for LSTM model."""
        X, y = [], []
        for i in range(len(df) - self.lookback):
            X.append(df.iloc[i:i+self.lookback].values)
            y.append(df.iloc[i+self.lookback, 0])  # Predicting price

        X, y = np.array(X), np.array(y)
        return train_test_split(X, y, test_size=0.2, random_state=42)

    def build_model(self):
        """Creates an LSTM-based neural network."""
        model = Sequential([
            LSTM(50, return_sequences=True, input_shape=(self.lookback, 3)),
            Dropout(0.2),
            LSTM(50, return_sequences=False),
            Dropout(0.2),
            Dense(25, activation="relu"),
            Dense(1)
        ])
        model.compile(optimizer="adam", loss="mse")
        return model

    def train_model_for_ticker(self, ticker):
        """Trains and saves an LSTM model for a given ETF."""
        df = self.load_data(ticker)
        if df is None:
            return  # Skip training if data is missing

        X_train, X_test, y_train, y_test = self.prepare_data(df)

        model = self.build_model()
        logging.info(f"Training model for {ticker}...")

        model.fit(X_train, y_train, validation_data=(X_test, y_test),
                  epochs=20, batch_size=16, verbose=1)

        model.save(f"{self.save_path}{ticker}_lstm.keras")  # ✅ Fix: Save model in Keras format
        logging.info(f"Model saved for {ticker} at {self.save_path}{ticker}_lstm.keras")

    def train_all_models(self):
        """Trains models for all selected ETFs."""
        for ticker in self.tickers:
            self.train_model_for_ticker(ticker)

if __name__ == "__main__":
    tickers = ["QQQ", "VGT", "SOXX", "ARKK", "SPY"]
    model_trainer = PredictiveModel(tickers)
    model_trainer.train_all_models()
    logging.info("All models trained successfully!")
