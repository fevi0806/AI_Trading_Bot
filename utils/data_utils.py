import yfinance as yf
import pandas as pd
import logging

logging.basicConfig(level=logging.INFO)

def fetch_historical_data(ticker, period="60d", interval="1h"):
    """Fetches historical stock data."""
    try:
        df = yf.download(ticker, period=period, interval=interval, auto_adjust=True)
        if df.empty:
            logging.error(f"❌ No data received for {ticker}")
            return None
        
        df = df[["Open", "High", "Low", "Close"]]
        logging.info(f"📈 Data Fetched for {ticker}, Shape: {df.shape}")
        return df
    except Exception as e:
        logging.error(f"❌ Error fetching data for {ticker}: {e}")
        return None
