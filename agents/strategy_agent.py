import zmq
import json
import time
import logging
import numpy as np
from stable_baselines3 import PPO
from utils.data_utils import fetch_historical_data
from utils.logger import setup_logger

class StrategyAgent:
    def __init__(self, comm_framework):
        self.comm = comm_framework
        self.trade_signal_pub = self.comm.create_publisher(5557)  # Trade Signal Publisher
        self.market_data_sub = self.comm.create_subscriber(5555)  # Market Data Subscriber
        self.logger = setup_logger("StrategyAgent")

    def load_ppo_model(self, ticker):
        """Loads a trained PPO model specific to the ticker."""
        model_path = f"models/{ticker}_ppo.zip"
        try:
            model = PPO.load(model_path)
            self.logger.info(f"📥 Loaded PPO model: {model_path}")
            return model
        except Exception as e:
            self.logger.error(f"❌ Failed to load model {model_path}: {e}")
            return None

    def predict_trade_signal(self, ticker):
        """Uses PPO model to predict a trade signal."""
        df = fetch_historical_data(ticker)
        if df is None or df.empty:
            self.logger.error(f"❌ No data received for {ticker}")
            return {"ticker": ticker, "signal": "HOLD"}

        df = df.iloc[-50:, [1, 2, 3]]  # Extract necessary features
        obs = np.array(df).reshape((1, 50, 3))

        model = self.load_ppo_model(ticker)
        if model is None:
            return {"ticker": ticker, "signal": "HOLD"}

        action, _ = model.predict(obs)
        action_index = int(action[0]) if isinstance(action, (list, np.ndarray)) else int(action)
        action_index = 0 if action_index not in [0, 1, 2] else action_index

        signal = ["HOLD", "BUY", "SELL"][action_index]
        self.logger.info(f"📊 {ticker} Predicted Signal: {signal}")

        return {"ticker": ticker, "signal": signal}

    def run(self):
        """Runs the strategy agent to send trade signals while considering risk."""
        tickers = ["SPY", "QQQ", "VGT", "SOXX", "ARKK"]
        while True:
            for ticker in tickers:
                signal = self.predict_trade_signal(ticker)
                self.trade_signal_pub.send_string(json.dumps(signal))
                self.logger.info(f"📡 Trade Signal Sent: {signal}")
                time.sleep(2)

if __name__ == "__main__":
    from agents.comm_framework import CommFramework
    agent = StrategyAgent(CommFramework())
    agent.run()
