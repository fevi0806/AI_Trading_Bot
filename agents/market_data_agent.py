import zmq
import json
import time
import logging
import os
import yfinance as yf
import pandas as pd
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from utils.logger import setup_logger
from agents.comm_framework import CommFramework

class MarketDataAgent:
    def __init__(self, comm_framework):
        self.comm = comm_framework
        self.publisher = self.comm.create_publisher("MarketDataAgent")

        if self.publisher is None:
            raise ValueError("❌ MarketDataAgent failed to initialize publisher. Check port assignments.")

        self.logger = setup_logger("MarketDataAgent", "logs/market_data_agent.log")
        self.tickers = ["QQQ", "SOXX", "SPY", "VGT", "ARKK"]

    def fetch_data(self, ticker):
        """Fetch historical market data for a given ticker."""
        try:
            data = yf.download(ticker, period="1y", interval="1d")
            if data.empty:
                self.logger.error(f"❌ No data available for {ticker}.")
                return None
            
            # Ensure 'Date' column exists
            if "Date" not in data.columns:
                data.reset_index(inplace=True)

            self.logger.info(f"📈 Fetched {ticker} data, Shape: {data.shape}")
            return data
        except Exception as e:
            self.logger.error(f"❌ Error fetching {ticker}: {e}")
            return None

    def run(self):
        """Continuously fetch and publish market data."""
        self.logger.info("🚀 Market Data Agent Started.")
        while True:
            for ticker in self.tickers:
                data = self.fetch_data(ticker)
                if data is not None:
                    market_data = data.copy()
                    market_data.columns = market_data.columns.map(str)  # Convert columns to string
                    market_data["Date"] = market_data["Date"].astype(str)  # Ensure Date is a string

                    try:
                        market_data_json = market_data.to_dict(orient="records")
                        json_message = json.dumps(market_data_json)
                        self.comm.send_message("MarketDataAgent", json_message)
                        self.logger.info(f"📤 Published {ticker} data successfully.")
                    except Exception as e:
                        self.logger.error(f"❌ JSON Serialization Error for {ticker}: {e}")

                time.sleep(60)  # Prevent API rate limits
            time.sleep(3600)  # Fetch new data every hour
