import pandas as pd
from agents.strategy_agent import StrategyAgent

class StrategyTester:
    def __init__(self):
        self.strategy_agent = StrategyAgent()  # ✅ No CommFramework

    def generate_signal(self, ticker, close_price):
        """Generate trade signals using StrategyAgent."""
        signal = self.strategy_agent.predict_trade_signal(ticker)
        
        # ✅ Ensure signal is valid
        if signal not in ["BUY", "SELL", "HOLD"]:
            signal = "HOLD"  # Default to HOLD if signal is invalid

        return signal

    def apply_strategy(self, ticker, data):
        """Apply the trading strategy to the dataset."""
        
        # ✅ Debugging: Print data before applying strategy
        print(f"\nMarket Data BEFORE strategy applied:\n{data.head()}")  

        signals = []

        for index, row in data.iterrows():
            signal = self.generate_signal(ticker, row["Close"])  # ✅ Pass close price for prediction
            signals.append(signal)

        # ✅ Add the 'Trade_Signal' column to the data
        data["Trade_Signal"] = signals

        # ✅ Debugging: Print data after adding 'Trade_Signal'
        print(f"\nMarket Data AFTER strategy applied:\n{data[['Close', 'Trade_Signal']].head()}")  

        return data
