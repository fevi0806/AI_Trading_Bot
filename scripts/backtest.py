import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from models.predictive_model import PredictiveModel
from utils.logger import setup_logger
# Initialize logger
logger = setup_logger()

class Backtest:
    def __init__(self, initial_balance=10000, trading_fee=0.001):
        self.balance = initial_balance
        self.trading_fee = trading_fee
        self.position = 0  # Number of shares held
        self.equity_curve = []

    def run_backtest(self):
        """
        Run a backtest using historical data and trade signals.
        """
        try:
            # Load historical data
            data_path = os.path.join(os.path.dirname(__file__), '../data/datasets/historical_data.csv')
            df = pd.read_csv(data_path)
            logger.info("Historical data loaded successfully.")

            # Convert 'date' to datetime and drop it
            df["date"] = pd.to_datetime(df["date"], errors="coerce")
            df = df.drop(columns=["date"])

            # Ensure all columns are numeric
            df = df.apply(pd.to_numeric, errors="coerce")

            # Drop any rows with NaN values
            df = df.dropna()

            # Separate features, target, and price
            X = df.drop(columns=["target", "price"])  # Features
            y = df["target"]  # Target variable (price movement)
            prices = df["price"]  # Asset prices

            # Split into training and testing sets
            split = int(0.8 * len(df))
            X_train, X_test = X[:split], X[split:]
            y_train, y_test = y[:split], y[split:]
            test_prices = prices[split:]  # Prices for testing period

            # ✅ Define input shape AFTER X_train is created
            input_shape = X_train.shape[1]
            model = PredictiveModel(input_shape=input_shape)  # ✅ Pass input shape when initializing

            # Train predictive model
            logger.info("Training predictive model...")
            model.train(X_train, y_train)

            # Make predictions
            logger.info("Running backtest...")
            predictions = model.predict(X_test)

            # Convert predictions to trade signals (1 = Buy, -1 = Sell)
            trade_signals = np.where(predictions.flatten() > 0, 1, -1)

            # Simulate trading
            self.simulate_trading(trade_signals, test_prices)

            # Save results
            backtest_results = pd.DataFrame({
                "Price": test_prices.values,
                "Signal": trade_signals,
                "Equity": self.equity_curve
            })
            backtest_results.to_csv("data/backtest_results.csv", index=False)
            logger.info("Backtest completed. Results saved to data/backtest_results.csv.")

            # Plot results
            self.plot_results(test_prices, trade_signals)

        except Exception as e:
            logger.error(f"Error during backtest: {e}")

    def simulate_trading(self, signals, prices):
        """
        Simulates trading based on model signals.
        """
        for i in range(len(signals)):
            price = prices.iloc[i]
            signal = signals[i]

            if signal == 1 and self.balance > price:  # Buy
                self.position = self.balance / price  # Buy max shares
                self.balance = 0
                logger.info(f"BUY at {price:.2f}, New Position: {self.position:.2f} shares")
            elif signal == -1 and self.position > 0:  # Sell
                self.balance = self.position * price  # Sell all shares
                self.position = 0
                self.balance *= (1 - self.trading_fee)  # Apply trading fee
                logger.info(f"SELL at {price:.2f}, New Balance: ${self.balance:.2f}")

            # Track equity (account balance + position value)
            equity = self.balance + (self.position * price)
            self.equity_curve.append(equity)

    def plot_results(self, prices, signals):
        """
        Plots equity curve and trade signals on price chart.
        """
        plt.figure(figsize=(12, 6))

        # Plot price
        plt.plot(prices.index, prices, label="Asset Price", color="black")

        # Plot buy & sell signals
        buy_signals = prices[signals == 1]
        sell_signals = prices[signals == -1]
        plt.scatter(buy_signals.index, buy_signals, marker="^", color="green", label="Buy", alpha=0.8)
        plt.scatter(sell_signals.index, sell_signals, marker="v", color="red", label="Sell", alpha=0.8)

        plt.title("Backtest: Price Chart with Trade Signals")
        plt.xlabel("Time")
        plt.ylabel("Price")
        plt.legend()
        plt.grid()
        plt.show()

if __name__ == "__main__":
    backtest = Backtest()
    backtest.run_backtest()
