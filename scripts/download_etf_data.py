import yfinance as yf
import pandas as pd
import os

# Define ETF tickers
etfs = ["QQQ", "VGT", "SOXX", "ARKK", "SPY"]

# Define date range
start_date = "2015-01-01"
end_date = "2024-01-01"

# Ensure the data folder exists
output_csv_path = "data/datasets/etf_data.csv"
os.makedirs(os.path.dirname(output_csv_path), exist_ok=True)

# Download and clean data
all_data = []

for etf in etfs:
    print(f"📥 Downloading data for {etf}...")
    df = yf.download(etf, start=start_date, end=end_date, auto_adjust=False)

    if df.empty:
        print(f"⚠️ No data found for {etf}, skipping...")
        continue

    # 🚨 Fix Multi-Index Columns: Flatten column names
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = ["_".join(col).strip() for col in df.columns.values]  # Convert MultiIndex to single level

    # Reset index and rename columns
    df.reset_index(inplace=True)
    df["Ticker"] = etf

    # 🚨 Debug: Print column names after flattening
    print(f"🛠️ Flattened Columns: {df.columns.tolist()}")

    # Correct column name mapping for each ETF
    expected_cols = {
        f"Open_{etf}": "Open",
        f"High_{etf}": "High",
        f"Low_{etf}": "Low",
        f"Close_{etf}": "Close",
        f"Adj Close_{etf}": "Close",  # Use Adjusted Close if available
        f"Volume_{etf}": "Volume",
    }

    # Rename only existing columns
    df.rename(columns={col: expected_cols[col] for col in expected_cols if col in df.columns}, inplace=True)

    # Keep only relevant columns
    df = df[["Date", "Open", "High", "Low", "Close", "Volume", "Ticker"]]

    # Fill missing price data instead of removing
    df.ffill(inplace=True)  # Forward fill missing values

    # Convert numeric columns properly
    for col in ["Open", "High", "Low", "Close", "Volume"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")  # Convert to numeric

    # 🚨 Debug: Check if there's valid data left
    if df.dropna(subset=["Close"]).empty:
        print(f"⚠️ Data for {etf} was empty after cleaning. Skipping...")
    else:
        all_data.append(df)

# Combine all ETF data into one DataFrame
if all_data:
    final_df = pd.concat(all_data, ignore_index=True)

    if not final_df.empty:
        final_df.to_csv(output_csv_path, index=False, sep=",", encoding="utf-8")
        print(f"✅ Downloaded and cleaned ETF data saved successfully: {output_csv_path}")
    else:
        print("❌ Data is still empty after processing. Check the script logic.")
else:
    print("❌ No valid data was downloaded. Check API response and ticker symbols.")
