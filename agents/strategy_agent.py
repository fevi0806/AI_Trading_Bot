import zmq
import json
import time
import logging
import os
import numpy as np
from stable_baselines3 import PPO
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from utils.logger import setup_logger
from agents.comm_framework import CommFramework

class StrategyAgent:
    def __init__(self, comm_framework):
        self.comm = comm_framework
        self.trade_signal_pub = self.comm.create_publisher("StrategyAgent")
        self.market_data_sub = self.comm.create_subscriber("StrategyAgent")
        self.logger = setup_logger("StrategyAgent", "logs/strategy_agent.log")

    def load_ppo_model(self, ticker):
        model_path = f"models/{ticker}_ppo.zip"
        if not os.path.exists(model_path):
            self.logger.error(f"❌ Model not found: {model_path}")
            return None
        try:
            model = PPO.load(model_path)
            self.logger.info(f"📥 Loaded Model: {model_path}")
            return model
        except Exception as e:
            self.logger.error(f"❌ Model Load Error: {e}")
            return None

    def predict_trade_signal(self, ticker):
        model = self.load_ppo_model(ticker)
        if model is None:
            return None
        signal = np.random.choice(["BUY", "SELL", "HOLD"])
        self.logger.info(f"📊 {ticker} Signal: {signal}")
        return signal

    def run(self):
        self.logger.info("🚀 Strategy Agent Started.")
        while True:
            try:
                message = self.market_data_sub.recv_string()
                market_data = json.loads(message)
                ticker = market_data[0].get("Ticker", "Unknown")
                signal = self.predict_trade_signal(ticker)

                if signal:
                    trade_signal = {"ticker": ticker, "signal": signal}
                    self.comm.send_message("StrategyAgent", json.dumps(trade_signal))
                    self.logger.info(f"📧 Trade Signal Sent: {trade_signal}")

            except Exception as e:
                self.logger.error(f"❌ Error in StrategyAgent: {e}")
            time.sleep(60)
