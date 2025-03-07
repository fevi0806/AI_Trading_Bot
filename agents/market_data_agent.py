import sys
import os
import time
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import yfinance as yf
import time
from utils.logger import setup_logger

class MarketDataAgent:
    def __init__(self, comm_framework):
        self.comm = comm_framework
        self.pub_socket = comm_framework.create_publisher(5555)

    def run(self):
        print("Market Data Agent Running...")

    def fetch_market_data(self, ticker="AAPL"):
        """
        Fetch real-time market data using Yahoo Finance and clean it.
        """
        # Fetch data
        data = yf.download(ticker, period="1d", interval="1m")

        # Clean the data
        data = data.droplevel(level=0, axis=1)  # Remove the "Price" level from columns
        data = data.reset_index()  # Reset the index to make "Datetime" a column
        data["Ticker"] = ticker  # Add a "Ticker" column

        return data

    def start(self):
        self.logger.info("Market Data Agent started.")
        while True:
            data = self.fetch_market_data()
            self.logger.info(f"Fetched market data: {data.tail(1)}")

            # Convert the last row to a JSON-serializable format
            last_row = data.iloc[-1]
            market_data = {
                "timestamp": last_row["Datetime"].isoformat(),  # Convert timestamp to string
                "ticker": last_row["Ticker"],                  # Add ticker
                "close": float(last_row["Close"]),             # Use float
                "high": float(last_row["High"]),               # Use float
                "low": float(last_row["Low"]),                 # Use float
                "open": float(last_row["Open"]),               # Use float
                "volume": int(last_row["Volume"])              # Use int
            }

            # Send market data
            self.comm_framework.send_market_data(market_data)

            # Add a delay (e.g., 60 seconds) before fetching new data
            time.sleep(60)