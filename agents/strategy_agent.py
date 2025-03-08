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

from utils.logger import setup_logger
from agents.comm_framework import CommFramework  # Correct import path

class StrategyAgent:
    def __init__(self, comm_framework):
        self.logger = setup_logger("StrategyAgent", "logs/strategy_agent.log")  # ✅ Ensure logging starts first
        self.logger.info("🛠 Initializing StrategyAgent...")  # ✅ Log before anything else
        
        self.comm = comm_framework
        self.trade_signal_pub = self.comm.create_publisher(5556)  # Trade Signal Publisher
        self.market_data_sub = self.comm.create_subscriber(5555)  # Market Data Subscriber

    def run(self):
        """Continuously receive market data and publish trade signals."""
        self.logger.info("🚀 Strategy Agent Started.")
        while True:
            try:
                message = self.market_data_sub.recv_string()
                self.logger.info(f"📥 Raw Market Data Received: {message[:500]}...")  # Log first 500 chars

                # ✅ Parse market data safely
                try:
                    market_data = json.loads(message)

                    if not isinstance(market_data, list) or not market_data:
                        raise ValueError(f"❌ Market data format is incorrect: {market_data}")

                    self.logger.info(f"✅ Parsed Market Data: {market_data[:2]}...")  # Log first 2 entries

                    # ✅ Extract Ticker Name from Column Keys
                    first_entry = market_data[0]
                    possible_tickers = [key.split("_")[-1] for key in first_entry.keys() if key.startswith("Close_")]
                    
                    if not possible_tickers:
                        raise ValueError(f"❌ No tickers found in market data keys: {list(first_entry.keys())}")

                    ticker = possible_tickers[0]  # Pick first detected ticker
                    self.logger.info(f"✅ Extracted Ticker: {ticker}")

                except Exception as e:
                    self.logger.error(f"❌ StrategyAgent Data Processing Error: {e}")
                    continue  # Skip this iteration to prevent a crash

            except Exception as e:
                self.logger.error(f"❌ StrategyAgent Error: {e}")
                continue  # Keep looping to log future errors

            time.sleep(60)  # Adjust frequency as needed
