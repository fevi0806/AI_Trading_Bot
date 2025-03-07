import pandas as pd
import numpy as np
import yfinance as yf
import logging
import os
from sklearn.preprocessing import MinMaxScaler

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

class DataPreprocessor:
    def __init__(self, tickers, period="5y", save_path="data/"):
        self.tickers = tickers
        self.period = period
        self.scaler = MinMaxScaler()
        self.save_path = save_path

        # Ensure the data directory exists
        os.makedirs(self.save_path, exist_ok=True)

    def fetch_data(self):
        """Downloads historical data for selected ETFs."""
        logging.info("Fetching historical market data...")
        data = {}

        for ticker in self.tickers:
            df = yf.download(ticker, period=self.period, auto_adjust=False)  # ✅ Fix: Disable auto-adjustment
            if df.empty:
                logging.warning(f"No data found for {ticker}")
                continue

            df["Adj Close"] = df["Close"]  # ✅ Explicitly define 'Adj Close' to avoid KeyError
            data[ticker] = df

            logging.info(f"Downloaded {len(df)} records for {ticker}")

        return data

    def preprocess_data(self, data):
        """Normalizes data and creates additional features."""
        processed_data = {}

        for ticker, df in data.items():
            logging.info(f"Processing data for {ticker}...")

            # Create additional features
            df["Returns"] = df["Adj Close"].pct_change()
            df["Volatility"] = df["Returns"].rolling(window=20).std()
            df.dropna(inplace=True)

            # Normalize features
            features = ["Adj Close", "Volume", "Volatility"]
            df_scaled = pd.DataFrame(self.scaler.fit_transform(df[features]), columns=features, index=df.index)

            processed_data[ticker] = df_scaled
            logging.info(f"Processed {len(df_scaled)} records for {ticker}")

        return processed_data

    def save_data(self, processed_data):
        """Saves preprocessed data as CSV files."""
        for ticker, df in processed_data.items():
            file_path = os.path.join(self.save_path, f"{ticker}_processed.csv")
            df.to_csv(file_path)
            logging.info(f"Saved processed data for {ticker} at {file_path}")

if __name__ == "__main__":
    tickers = ["QQQ", "VGT", "SOXX", "ARKK", "SPY"]
    preprocessor = DataPreprocessor(tickers)
    
    raw_data = preprocessor.fetch_data()
    processed_data = preprocessor.preprocess_data(raw_data)
    preprocessor.save_data(processed_data)

    logging.info("Data preprocessing completed successfully!")
