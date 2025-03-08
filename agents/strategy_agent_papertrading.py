import os
import sys
import time
import logging
import numpy as np
import pandas as pd
import zmq
import yfinance as yf
from stable_baselines3 import PPO

# Ensure utils module is found
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from utils.data_utils import preprocess_data
# ✅ Configure logging with UTF-8 support for Windows compatibility
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("logs/strategy_agent.log", encoding="utf-8"),
        logging.StreamHandler()
    ],
)
class StrategyAgent:
    def __init__(self):
        """Initialize the strategy agent, set up logging, and load models."""
        self.logger = logging.getLogger(__name__)
        logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

        self.tickers = ["QQQ", "VGT", "SOXX", "ARKK", "SPY"]
        self.models = {}
        self.load_models()

        # ZeroMQ Setup
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.PUB)
        self.socket.bind("tcp://127.0.0.1:5556")
        logging.info(" ZeroMQ Bound to tcp://127.0.0.1:5560")

    def load_models(self):
        """Load trained PPO models for each ETF."""
        for ticker in self.tickers:
            try:
                self.models[ticker] = PPO.load(f"models/{ticker}_ppo.zip")
                self.logger.info(f"✅ Loaded PPO model for {ticker}.")
            except Exception as e:
                self.logger.error(f" Could not load PPO model for {ticker}: {e}")

    def get_market_data(self, ticker):
        """Fetch market data, ensure correct preprocessing, and reshape for PPO input."""
        try:
            df = yf.download(ticker, period="60d", interval="1h", auto_adjust=False)  # Fix for YF update
            df.dropna(inplace=True)

            # Ensure correct feature selection for PPO model (modify if needed)
            features = ["Open", "High", "Low"]
            df = df[features]

            # Validate data length
            if len(df) < 50:
                self.logger.error(f" Not enough historical data for {ticker}. Minimum 50 time steps required.")
                return np.zeros((50, 3))  # Return empty array for safety

            df = df[-50:]  # Select last 50 time steps
            df = df.to_numpy().reshape(50, 3)  # Ensure correct shape

            return df  # Return NumPy array

        except Exception as e:
            self.logger.error(f" Failed to fetch data for {ticker}: {e}")
            return np.zeros((50, 3))  # Handle failures safely

    def predict_trade_signal(self, ticker):
        """Use the trained PPO model to predict a trade signal based on market data."""
        try:
            obs = self.get_market_data(ticker)

            if isinstance(obs, np.ndarray) and obs.shape == (50, 3):
                action, _ = self.models[ticker].predict(obs, deterministic=True)
                action_map = {0: "BUY", 1: "SELL", 2: "HOLD"}
                return {"ticker": ticker, "signal": action_map.get(int(action), "HOLD")}
            else:
                self.logger.error(f" Observation shape {obs.shape} is invalid for PPO. Expected (50,3).")
                return {"ticker": ticker, "signal": "HOLD"}

        except Exception as e:
            self.logger.error(f" Error predicting trade signal for {ticker}: {e}")
            return {"ticker": ticker, "signal": "HOLD"}

    def run(self):
        """Main loop to fetch market data, generate trade signals, and publish them via ZeroMQ."""
        self.logger.info(" Strategy Agent Initialized and Running...")
        while True:
            for ticker in self.tickers:
                signal = self.predict_trade_signal(ticker)
                self.logger.info(f" Trade Signal Sent: {signal}")
                self.socket.send_json(signal)

            time.sleep(60)  # Evaluate market every minute

if __name__ == "__main__":
    agent = StrategyAgent()
    agent.run()
