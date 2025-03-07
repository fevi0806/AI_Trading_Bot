import pandas as pd
import numpy as np
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

tickers = ["QQQ", "VGT", "SOXX", "ARKK", "SPY"]

for ticker in tickers:
    file_path = f"data/{ticker}_processed.csv"
    df = pd.read_csv(file_path, index_col=0)
    
    if df.isnull().values.any():
        logging.warning(f"❌ NaN values detected in {ticker} data!")
        df.fillna(method="ffill", inplace=True)  # Forward-fill missing values
        df.fillna(method="bfill", inplace=True)  # Backward-fill remaining NaN
        df.to_csv(file_path)
        logging.info(f"✅ Fixed NaN values in {ticker}.")
    else:
        logging.info(f"✅ {ticker} data is clean!")
