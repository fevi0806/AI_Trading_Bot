import pandas as pd
import numpy as np
import json
import time
import logging
import os
import sys
import yfinance as yf

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backtesting.strategy_tester import StrategyTester
from backtesting.backtest_engine import BacktestEngine

# ✅ Initialize standard logger (removing `get_logger`)
logger = logging.getLogger("backtesting")
logger.setLevel(logging.INFO)

# ✅ Ensure logs appear in the console
console_handler = logging.StreamHandler()
console_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
logger.addHandler(console_handler)

# ✅ Define parameters
SYMBOL = "QQQ"
START_DATE = "2023-01-01"
END_DATE = "2023-12-31"
INITIAL_CAPITAL = 10000

def main():
    print("🚀 Iniciando Backtesting...")

    # ✅ Initialize StrategyTester
    strategy = StrategyTester()

    # ✅ Initialize Backtest Engine
    backtest = BacktestEngine(INITIAL_CAPITAL)

    # ✅ Fetch and process data
    logger.info(f"📥 Downloading historical data for {SYMBOL} from {START_DATE} to {END_DATE}...")
    market_data = yf.download(SYMBOL, start=START_DATE, end=END_DATE)

    if market_data.empty:
        logger.error(f"❌ No market data found for {SYMBOL}. Exiting backtest.")
        return

    # Debugging: Print market data before applying the strategy
    logger.info(f"✅ Historical data for {SYMBOL} retrieved successfully, Shape: {market_data.shape}")
    print(f"\nMarket Data Loaded:\n{market_data.head()}")  # Debugging

    # ✅ Apply strategy and generate trade signals
    market_data = strategy.apply_strategy(SYMBOL, market_data)

    # ✅ Debugging: Check if 'Trade_Signal' exists
    if "Trade_Signal" not in market_data.columns:
        logger.error("❌ 'Trade_Signal' column is missing after strategy application.")
        print("❌ 'Trade_Signal' column is missing. Debugging needed!")
        return

    # ✅ Debugging: Print market data after applying strategy
    print(f"\nMarket Data after strategy applied:\n{market_data[['Close', 'Trade_Signal']].head()}")

    # ✅ Run the backtest
    try:
        backtest.run_backtest(market_data)
    except Exception as e:
        logger.error(f"❌ Error running backtest: {e}")
        return

    # ✅ Display results
    results = backtest.get_results()
    print("\nResultados del Backtesting:")
    for key, value in results.items():
        print(f"{key}: {value}")

if __name__ == "__main__":
    main()
