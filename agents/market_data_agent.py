import zmq
import json
import time
import os
import yfinance as yf
import pandas as pd
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from utils.logger import get_logger
from agents.comm_framework import CommFramework

class MarketDataAgent:
    def __init__(self, comm_framework=None):
        self.comm = comm_framework if comm_framework else None
        self.logger = get_logger("trading")
        self.tickers = ["QQQ", "SOXX", "SPY", "VGT", "ARKK"]
        self.running = True  

    def fetch_data(self, ticker):
        """Fetch real-time market data from Yahoo Finance."""
        try:
            if not self.running:
                return None  

            self.logger.log("info", f"Fetching data for {ticker}...")
            data = yf.download(ticker, period="1y", interval="1d")

            if data.empty:
                self.logger.log("warning", f"No data found for {ticker}.")
                return None

            self.logger.log("info", f"Data fetched for {ticker}, Shape: {data.shape}")

            data.reset_index(inplace=True)
            if "Date" not in data.columns:
                if "index" in data.columns:
                    data.rename(columns={"index": "Date"}, inplace=True)
                else:
                    self.logger.log("error", f"Missing 'Date' column for {ticker}. Columns: {list(data.columns)}")
                    return None

            data["Date"] = data["Date"].astype(str)
            data.columns = [str(col) for col in data.columns]  

            return data
        except IOError as io_err:
            self.logger.log("error", f"I/O Error fetching {ticker}: {io_err}")
            return None
        except Exception as e:
            self.logger.log("error", f"Unexpected error fetching {ticker}: {e}")
            return None

    def get_historical_data(self, symbol, start_date, end_date):
        """Fetch historical market data from Yahoo Finance and fix Multi-Index column structure."""
        try:
            self.logger.log("info", f"Downloading historical data for {symbol} from {start_date} to {end_date}...")

            data = yf.download(symbol, start=start_date, end=end_date, interval="1d", auto_adjust=False)

            if data.empty:
                self.logger.log("warning", f"No historical data found for {symbol}.")
                return None

            # If data has a Multi-Index, drop the first level
            if isinstance(data.columns, pd.MultiIndex):
                data.columns = data.columns.get_level_values(0)  # Keep only the price type (e.g., 'Close', 'Open')

            # Ensure 'Close' column exists
            if "Close" not in data.columns and "Adj Close" in data.columns:
                self.logger.log("warning", f"'Close' column missing, using 'Adj Close' for {symbol}.")
                data.rename(columns={"Adj Close": "Close"}, inplace=True)

            if "Close" not in data.columns:
                self.logger.log("error", f"Final check: 'Close' column is missing for {symbol}. Data columns: {list(data.columns)}")
                return None

            data.reset_index(inplace=True)
            data["Date"] = data["Date"].astype(str)
            data.columns = [str(col) for col in data.columns]  

            self.logger.log("info", f"Historical data for {symbol} retrieved successfully, Shape: {data.shape}")
            return data

        except Exception as e:
            self.logger.log("error", f"Error retrieving historical data for {symbol}: {e}")
            return None

    def run(self):
        """Fetch and publish market data continuously."""
        self.logger.log("info", "Market Data Agent started.")

        while self.running:  
            for ticker in self.tickers:
                if not self.running:
                    break  
                
                data = self.fetch_data(ticker)
                if data is not None:
                    try:
                        market_data_json = data.to_dict(orient="records")
                        json_message = json.dumps(market_data_json)

                        if self.publisher and not self.publisher.closed:
                            self.publisher.send_string(json_message)
                            self.logger.log("info", f"Published {ticker} data successfully.")
                        else:
                            self.logger.log("warning", f"Cannot publish {ticker} data: Publisher socket closed.")
                    except zmq.error.ZMQError as zmq_err:
                        self.logger.log("error", f"ZeroMQ Error while publishing {ticker}: {zmq_err}")
                    except Exception as e:
                        self.logger.log("error", f"JSON Serialization Error for {ticker}: {e}")

                time.sleep(60)  

            self.logger.log("info", "Waiting 1 hour before next data fetch...")
            time.sleep(3600)  

    def stop(self):
        """Gracefully stop the agent."""
        self.logger.log("info", "Stopping Market Data Agent...")
        self.running = False  
