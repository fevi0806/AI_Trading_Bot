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
        self.logger = setup_logger("MarketDataAgent", "logs/market_data_agent.log")
        self.tickers = ["QQQ", "SOXX", "SPY", "VGT", "ARKK"]

    def fetch_data(self, ticker):
        """Fetch market data from Yahoo Finance and format it properly."""
        try:
            data = yf.download(ticker, period="1y", interval="1d")
            if data.empty:
                self.logger.error(f"❌ No data for {ticker}.")
                return None

            self.logger.info(f"📈 Fetched {ticker} data, Shape: {data.shape}")

            # ✅ Ensure "Date" column exists and is properly formatted
            data.reset_index(inplace=True)

            # ✅ Explicitly rename the "Date" column
            if "Date" not in data.columns:
                if "index" in data.columns:
                    data.rename(columns={"index": "Date"}, inplace=True)
                else:
                    self.logger.error(f"❌ 'Date' column missing for {ticker} data. Current columns: {list(data.columns)}")
                    return None

            # ✅ Convert Date column to string for JSON serialization
            data["Date"] = data["Date"].astype(str)

            # ✅ Convert column names to strings (Fixes tuple keys issue)
            data.columns = [str(col) for col in data.columns]

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
                    try:
                        # ✅ Convert data to JSON
                        market_data_json = data.to_dict(orient="records")
                        json_message = json.dumps(market_data_json)

                        # ✅ Send JSON message via publisher
                        self.publisher.send_string(json_message)
                        self.logger.info(f"📤 Published {ticker} data successfully.")
                    except Exception as e:
                        self.logger.error(f"❌ JSON Serialization Error for {ticker}: {e}")

                time.sleep(60)  # Delay to avoid API limits
            time.sleep(3600)  # Fetch new data every hour
