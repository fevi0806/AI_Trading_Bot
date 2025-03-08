import zmq
import json
import time
import logging
import os
import numpy as np
from stable_baselines3 import PPO

# Ensure Python can find the parent directory
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from utils.data_utils import fetch_historical_data
from utils.logger import setup_logger
from agents.comm_framework import CommFramework  # Correct import path

class StrategyAgent:
    def __init__(self, comm_framework):
        self.comm = comm_framework
        self.trade_signal_pub = self.comm.create_publisher(5557)  # Trade Signal Publisher
        self.market_data_sub = self.comm.create_subscriber(5555)  # Market Data Subscriber
        self.logger = setup_logger("StrategyAgent", "logs/strategy_agent.log")

    def load_ppo_model(self, ticker):
        """Loads a trained PPO model specific to the ticker."""
        model_path = f"models/{ticker}_ppo.zip"
        if not os.path.exists(model_path):
            self.logger.error(f"❌ Model file not found: {model_path}")
            return None
        try:
            model = PPO.load(model_path)
            self.logger.info(f"📥 Loaded PPO model: {model_path}")
            return model
        except Exception as e:
            self.logger.error(f"❌ Failed to load model {model_path}: {e}")
            return None

    def predict_trade_signal(self, ticker):
        """Uses PPO model to predict a trade signal."""
        model = self.load_ppo_model(ticker)
        if model is None:
            self.logger.error(f"❌ No model available for {ticker}. Cannot predict trade signal.")
            return None
        # Example: Generate a random signal
        signal = np.random.choice(["BUY", "SELL", "HOLD"])
        self.logger.info(f"📊 {ticker} Predicted Signal: {signal} | Model Loaded: {model is not None}")
        return signal

    def run(self):
        """Continuously receive market data and publish trade signals."""
        self.logger.info("🚀 Strategy Agent Started.")
        while True:
            try:
                message = self.market_data_sub.recv_string()
                self.logger.info(f"📥 Raw Market Data Received: {message}")  # Debugging incoming data

                # Parse market data safely
                try:
                    market_data = json.loads(message)
                    if not isinstance(market_data, list) or not market_data:
                        raise ValueError("Market data format is incorrect or empty.")

                    self.logger.info(f"✅ Parsed Market Data: {market_data}")

                    ticker = market_data[0].get("Ticker")
                    if not ticker:
                        raise ValueError("❌ Missing 'Ticker' in market data.")

                    self.logger.info(f"✅ Extracted Ticker: {ticker}")

                except Exception as e:
                    self.logger.error(f"❌ Error parsing market data: {e}")
                    continue  # Skip this iteration if data is bad

                signal = self.predict_trade_signal(ticker)
                if signal:
                    trade_signal = {"ticker": ticker, "signal": signal}
                    self.trade_signal_pub.send_json(trade_signal)
                    self.logger.info(f"📧 Trade Signal Sent: {trade_signal}")

            except Exception as e:
                self.logger.error(f"❌ Error in StrategyAgent run loop: {e}")
            time.sleep(60)  # Adjust frequency as needed
