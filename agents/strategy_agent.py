import zmq
import json
import time
import logging
import numpy as np
import os
import sys


# Ensure utils module is found
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from stable_baselines3 import PPO
from utils.data_utils import fetch_historical_data

logging.basicConfig(level=logging.INFO)

class StrategyAgent:
    def __init__(self):
        self.context = zmq.Context()
        
        # PUB socket to send trade signals
        self.trade_socket = self.context.socket(zmq.PUB)
        self.trade_socket.connect("tcp://localhost:5557")

        # SUB socket to receive execution feedback
        self.execution_socket = self.context.socket(zmq.SUB)
        self.execution_socket.connect("tcp://localhost:5559")
        self.execution_socket.setsockopt_string(zmq.SUBSCRIBE, "")

        self.models = self.load_models()
        logging.info("✅ Strategy Agent Initialized")

    def load_models(self):
        """Loads PPO models for each ticker."""
        tickers = ["QQQ", "VGT", "SOXX", "ARKK", "SPY"]
        models = {}
        for ticker in tickers:
            model_path = f"models/{ticker}_ppo.zip"
            try:
                models[ticker] = PPO.load(model_path)
                logging.info(f"📥 Loaded model for {ticker}")
            except Exception as e:
                logging.error(f"❌ Failed to load {ticker} model: {e}")
        return models

    def predict_trade_signal(self, ticker):
        """Generates a trade signal using PPO model."""
        df = fetch_historical_data(ticker)

        # Ensure there are enough rows
        if df.shape[0] < 50:
            logging.warning(f"⚠️ Not enough data for {ticker}. Expected 50, got {df.shape[0]}. Defaulting to HOLD.")
            return {"ticker": ticker, "signal": "HOLD"}

        # Ensure correct column selection
        expected_cols = ["Open", "High", "Low"]
        if not all(col in df.columns for col in expected_cols):
            logging.error(f"❌ Missing required columns in {ticker} data: {df.columns}")
            return {"ticker": ticker, "signal": "HOLD"}

        df = df[expected_cols].iloc[-50:]  # Extract only needed columns
        obs = df.to_numpy().reshape((1, 50, 3))

        model = self.models.get(ticker)
        if model is None:
            logging.warning(f"⚠️ No model for {ticker}, defaulting to HOLD")
            return {"ticker": ticker, "signal": "HOLD"}

        action, _ = model.predict(obs)
        signal = ["HOLD", "BUY", "SELL"][int(action)]
        return {"ticker": ticker, "signal": signal}

    def run(self):
        """Main loop to generate trade signals."""
        tickers = ["QQQ", "VGT", "SOXX", "ARKK", "SPY"]
        while True:
            for ticker in tickers:
                signal = self.predict_trade_signal(ticker)
                self.trade_socket.send_string(json.dumps(signal))
                logging.info(f"📡 Trade Signal Sent: {signal}")
                time.sleep(1)

if __name__ == "__main__":
    agent = StrategyAgent()
    agent.run()
