import os
import sys
import time
import logging
import pandas as pd
import yfinance as yf
import numpy as np
import zmq

# Ensure utils module is found
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from stable_baselines3 import PPO
from utils.data_utils import fetch_historical_data, preprocess_data

# Logging Configuration
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

class StrategyAgent:
    def __init__(self):
        logging.info("📡 Initializing Strategy Agent...")

        self.tickers = ["QQQ", "VGT", "SOXX", "ARKK", "SPY"]
        self.models = {}

        # Load Models
        for ticker in self.tickers:
            try:
                self.models[ticker] = PPO.load(f"models/{ticker}_ppo.zip")
                logging.info(f"✅ Loaded model for {ticker}")
            except Exception as e:
                logging.error(f"❌ Failed to load model for {ticker}: {e}")
                self.models[ticker] = None

        # ZMQ Configuration
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.PUB)
        self.socket.bind("tcp://127.0.0.1:5556")
        logging.info("✅ ZMQ Publisher bound to tcp://127.0.0.1:5556")

    def predict_trade_signal(self, ticker):
        """Fetch market data, preprocess it, and generate a trade signal."""
        logging.info(f"📡 Fetching historical data for {ticker}...")

        df = fetch_historical_data(ticker)
        if df is None:
            logging.warning(f"⚠️ No data for {ticker}, skipping signal.")
            return {"ticker": ticker, "signal": "HOLD"}

        df = preprocess_data(df)
        if df is None or df.shape != (50, 3):
            logging.error(f"❌ Unexpected data shape {df.shape if df is not None else None} for {ticker}, expected (50,3).")
            return {"ticker": ticker, "signal": "HOLD"}

        obs = df.to_numpy().reshape((1, 50, 3))  # Ensure correct shape

        # Ensure Model Exists
        if self.models[ticker] is None:
            logging.warning(f"⚠️ No trained model available for {ticker}. Sending HOLD signal.")
            return {"ticker": ticker, "signal": "HOLD"}

        # Predict Action
        action, _ = self.models[ticker].predict(obs, deterministic=True)
        if not isinstance(action, np.ndarray) or action.size == 0:
            logging.error(f"❌ Invalid model output for {ticker}: {action}")
            return {"ticker": ticker, "signal": "HOLD"}

        action_index = int(action[0])  # Convert NumPy scalar to Python int
        if action_index not in [0, 1, 2]:
            logging.warning(f"⚠️ Invalid action index {action_index}, defaulting to HOLD.")
            action_index = 0

        signal = ["HOLD", "BUY", "SELL"][action_index]
        logging.info(f"📡 Trade Signal Sent: {{'ticker': '{ticker}', 'signal': '{signal}'}}")

        return {"ticker": ticker, "signal": signal}

    def run(self):
        """Continuously fetch market data and send trade signals via ZMQ."""
        logging.info("🚀 Strategy Agent Running...")
        while True:
            for ticker in self.tickers:
                trade_signal = self.predict_trade_signal(ticker)
                self.socket.send_json(trade_signal)
                time.sleep(1)  # Avoid overwhelming the execution agent
            time.sleep(10)  # Re-evaluate every 10 seconds

if __name__ == "__main__":
    agent = StrategyAgent()
    agent.run()
