import pandas as pd
import numpy as np

def preprocess_data(df):
    """ Preprocess market data to be used as input for PPO models. """
    if df is None or df.empty:
        raise ValueError("❌ Received empty DataFrame in preprocess_data.")

    df = df.copy()
    
    # Ensure required columns exist
    required_cols = ["Open", "High", "Low", "Close", "Volume"]
    missing_cols = [col for col in required_cols if col not in df.columns]
    if missing_cols:
        raise ValueError(f"❌ Missing required columns: {missing_cols}")

    # Convert timestamp to datetime (if not already)
    if not isinstance(df.index, pd.DatetimeIndex):
        df.index = pd.to_datetime(df.index)

    # Calculate technical indicators (example: moving averages)
    df["MA_5"] = df["Close"].rolling(window=5).mean()
    df["MA_10"] = df["Close"].rolling(window=10).mean()
    
    # Drop NaN values after calculations
    df.dropna(inplace=True)

    # Normalize data
    df_normalized = (df - df.min()) / (df.max() - df.min())

    # Ensure return type is DataFrame
    return pd.DataFrame(df_normalized)
