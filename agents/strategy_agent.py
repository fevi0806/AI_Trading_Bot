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

# Setup Logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

class StrategyAgent:
    def __init__(self, comm_framework):
        self.comm = comm_framework
        self.trade_signal_pub = self.context.socket(zmq.PUB)
        self.trade_signal_pub.bind("tcp://*:5557")  # Corrected port usage

        logging.info("✅ Strategy Agent Initialized")

    def load_ppo_model(self, ticker):
        """Loads the trained PPO model specific to the ticker."""
        model_path = f"models/{ticker}_ppo.zip"
        try:
            model = PPO.load(model_path)
            logging.info(f"📥 Loaded PPO model: {model_path}")
            return model
        except Exception as e:
            logging.error(f"❌ Failed to load model {model_path}: {e}")
            return None

    def predict_trade_signal(self, ticker):
        """Predicts a trade signal using the PPO model."""
        df = fetch_historical_data(ticker)
        if df is None or df.empty:
            logging.error(f"❌ No data received for {ticker}")
            return {"ticker": ticker, "signal": "HOLD"}

        df = df.iloc[-50:, [1, 2, 3]]  # Extract relevant columns
        obs = np.array(df).reshape((1, 50, 3))

        model = self.load_ppo_model(ticker)
        if model is None:
            return {"ticker": ticker, "signal": "HOLD"}

        action, _ = model.predict(obs)

        action_index = int(action[0]) if isinstance(action, (list, np.ndarray)) else int(action)

        if action_index not in [0, 1, 2]:
            logging.warning(f"⚠️ Invalid action index {action_index}, defaulting to HOLD")
            action_index = 0  

        signal = ["HOLD", "BUY", "SELL"][action_index]
        logging.info(f"📊 {ticker} Predicted Signal: {signal}")

        return {"ticker": ticker, "signal": signal}

    def run(self):
        """Runs the strategy agent to send trade signals."""
        tickers = ["SPY", "QQQ", "VGT", "SOXX", "ARKK"]
        while True:
            for ticker in tickers:
                signal = self.predict_trade_signal(ticker)
                self.trade_signal_pub.send_string(json.dumps(signal))
                logging.info(f"📡 Trade Signal Sent: {signal}")
                time.sleep(2)

if __name__ == "__main__":
    agent = StrategyAgent()
    agent.run()
