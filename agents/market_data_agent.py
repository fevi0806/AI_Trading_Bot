import sys
import os
import time
import yfinance as yf
import json
import logging
from utils.logger import setup_logger

class MarketDataAgent:
    def __init__(self, comm_framework):
        self.comm = comm_framework
        self.pub_socket = self.comm.create_publisher(5555)  # Market Data Publisher
        self.logger = setup_logger("MarketDataAgent")

    def fetch_market_data(self, ticker="AAPL"):
        """
        Fetch market data using Yahoo Finance (for both real-time & historical data).
        """
        try:
            data = yf.download(ticker, period="1d", interval="1m")
            data = data.droplevel(level=0, axis=1)  # Remove the "Price" level from columns
            data = data.reset_index()
            data["Ticker"] = ticker
            return data
        except Exception as e:
            self.logger.error(f"❌ Failed to fetch market data: {e}")
            return None

    def run(self):
        """
        Continuously fetch market data and send it over ZMQ.
        """
        self.logger.info("🚀 Market Data Agent Started.")
        tickers = ["SPY", "QQQ", "VGT", "SOXX", "ARKK"]

        while True:
            for ticker in tickers:
                data = self.fetch_market_data(ticker)
                if data is not None:
                    last_row = data.iloc[-1]
                    market_data = {
                        "timestamp": last_row["Datetime"].isoformat(),
                        "ticker": last_row["Ticker"],
                        "close": float(last_row["Close"]),
                        "high": float(last_row["High"]),
                        "low": float(last_row["Low"]),
                        "open": float(last_row["Open"]),
                        "volume": int(last_row["Volume"])
                    }

                    self.pub_socket.send_string(json.dumps(market_data))
                    self.logger.info(f"📡 Market Data Sent: {market_data}")
                
                time.sleep(5)  # Fetch data every 5 seconds (adjustable)

if __name__ == "__main__":
    from agents.comm_framework import CommFramework
    agent = MarketDataAgent(CommFramework())
    agent.run()
