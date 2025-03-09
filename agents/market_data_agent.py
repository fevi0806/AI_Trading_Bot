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

        # ✅ Ensure logging is initialized correctly with proper file handling
        log_file_path = os.path.join(os.path.dirname(__file__), "..", "logs", "market_data_agent.log")
        self.logger = setup_logger("MarketDataAgent", log_file_path)

        self.tickers = ["QQQ", "SOXX", "SPY", "VGT", "ARKK"]
        self.running = True  # ✅ Allows graceful shutdown

    def fetch_data(self, ticker):
        """Fetch market data from Yahoo Finance and format it properly."""
        try:
            if not self.running:
                return None  # ✅ Stop fetching if shutting down

            self.logger.info(f"🔍 Fetching data for {ticker}...")
            data = yf.download(ticker, period="1y", interval="1d")

            if data.empty:
                self.logger.warning(f"⚠️ No data found for {ticker}.")
                return None

            self.logger.info(f"📈 Successfully fetched {ticker} data, Shape: {data.shape}")

            # ✅ Ensure "Date" column exists and is properly formatted
            data.reset_index(inplace=True)

            # ✅ Explicitly rename the "Date" column
            if "Date" not in data.columns:
                if "index" in data.columns:
                    data.rename(columns={"index": "Date"}, inplace=True)
                else:
                    self.logger.error(f"❌ 'Date' column missing for {ticker}. Columns: {list(data.columns)}")
                    return None

            # ✅ Convert Date column to string for JSON serialization
            data["Date"] = data["Date"].astype(str)

            # ✅ Convert column names to strings (Fixes tuple keys issue)
            data.columns = [str(col) for col in data.columns]

            return data
        except IOError as io_err:
            self.logger.error(f"❌ I/O Error fetching {ticker}: {io_err}")
            return None
        except Exception as e:
            self.logger.error(f"❌ Unexpected error fetching {ticker}: {e}")
            return None

    def run(self):
        """Continuously fetch and publish market data until stopped."""
        self.logger.info("🚀 Market Data Agent Started.")

        while self.running:  # ✅ Check shutdown flag
            for ticker in self.tickers:
                if not self.running:
                    break  # ✅ Exit if shutdown is requested
                
                data = self.fetch_data(ticker)
                if data is not None:
                    try:
                        # ✅ Convert data to JSON safely
                        market_data_json = data.to_dict(orient="records")
                        json_message = json.dumps(market_data_json)

                        # ✅ Ensure publisher is still available before sending
                        if self.publisher and not self.publisher.closed:
                            self.publisher.send_string(json_message)
                            self.logger.info(f"📤 Published {ticker} data successfully.")
                        else:
                            self.logger.warning(f"⚠️ Cannot publish {ticker} data: Publisher socket closed.")
                    except zmq.error.ZMQError as zmq_err:
                        self.logger.error(f"❌ ZeroMQ Error while publishing {ticker}: {zmq_err}")
                    except Exception as e:
                        self.logger.error(f"❌ JSON Serialization Error for {ticker}: {e}")

                time.sleep(60)  # ✅ Delay to avoid API limits

            self.logger.info("⏳ Waiting 1 hour before next data fetch...")
            time.sleep(3600)  # ✅ Fetch new data every hour

    def stop(self):
        """Gracefully stop the agent's execution."""
        self.logger.info("🛑 Stopping Market Data Agent...")
        self.running = False  # ✅ Signal the loop to exit
