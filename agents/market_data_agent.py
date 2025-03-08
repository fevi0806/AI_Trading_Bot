import zmq
import json
import time
import logging
import os
import yfinance as yf
import pandas as pd

# Ensure Python can find the parent directory
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from utils.logger import setup_logger
from agents.comm_framework import CommFramework  # Correct import path

class MarketDataAgent:
    def __init__(self, comm_framework):
        self.comm = comm_framework
        self.publisher = self.comm.create_publisher(5555)  # Market Data Publisher
        self.logger = setup_logger("MarketDataAgent", "logs/market_data_agent.log")
        self.tickers = ["QQQ", "SOXX", "SPY", "VGT", "ARKK"]  # ✅ Updated tickers

    def fetch_data(self, ticker):
        """Fetch historical market data for a given ticker."""
        try:
            data = yf.download(ticker, period="1y", interval="1d")
            if data.empty:
                self.logger.error(f"❌ No data fetched for {ticker}.")
                return None
            self.logger.info(f"📈 Data Fetched for {ticker}, Shape: {data.shape}")
            return data
        except Exception as e:
            self.logger.error(f"❌ Error fetching data for {ticker}: {e}")
            return None

    def run(self):
        """Continuously fetch market data and publish it."""
        self.logger.info("🚀 Market Data Agent Started.")
        while True:
            for ticker in self.tickers:
                data = self.fetch_data(ticker)
                if data is not None:
                    market_data = data.reset_index()

                    # ✅ Ensure the first column is explicitly named 'Date'
                    if market_data.columns[0] != "Date":
                        market_data.rename(columns={market_data.columns[0]: "Date"}, inplace=True)

                    # ✅ Verify 'Date' column exists before proceeding
                    if "Date" not in market_data.columns:
                        self.logger.error(f"❌ Missing 'Date' column in fetched data for {ticker}. Skipping...")
                        continue

                    market_data.columns = market_data.columns.map(str)  # Convert columns to strings
                    market_data["Date"] = market_data["Date"].astype(str)  # Convert timestamps to string

                    try:
                        market_data_json = market_data.to_dict(orient="records")
                        json_message = json.dumps(market_data_json)
                        self.publisher.send_string(json_message)
                        self.logger.info(f"📤 Published data for {ticker}")
                    except Exception as e:
                        self.logger.error(f"❌ JSON Serialization Error for {ticker}: {e}")
                time.sleep(60)  # Fetch data every 60 seconds
            time.sleep(3600)  # Fetch new data every hour
