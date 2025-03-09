import pandas as pd
import requests
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


from datetime import datetime
from agents.market_data_agent import MarketDataAgent
from backtesting.performance_metrics import PerformanceMetrics
from utils.logger import backtest_logger

class BacktestEngine:
    def __init__(self, initial_cash=10000, commission=0.001):
        self.initial_cash = initial_cash
        self.commission = commission
        self.cash = initial_cash
        self.positions = 0
        self.trade_log = []
        self.data = None

    def load_data(self, symbol, start_date, end_date):
        """Load historical data and ensure correct format"""
        market_data = MarketDataAgent(comm_framework=None)
        self.data = market_data.get_historical_data(symbol, start_date, end_date)

        if self.data is None or self.data.empty:
            backtest_logger.log("error", f"Failed to load data for {symbol}. Exiting backtest.")
            raise ValueError(f"No data available for {symbol}.")

        # Debugging: Check the type and content of 'Close' column
        print("DEBUG - Close Column Type:", type(self.data["Close"]))
        print("DEBUG - Close Column Head:\n", self.data["Close"].head())

        # Ensure 'Close' is a single column (Series), not a DataFrame
        if isinstance(self.data["Close"], pd.DataFrame):
            print("DEBUG - Extracting single column from Close DataFrame...")
            self.data["Close"] = self.data["Close"].iloc[:, 0]  # Extract first column if duplicated

        # Calculate returns
        self.data['Returns'] = self.data['Close'].pct_change()

        backtest_logger.log("info", f"Data for {symbol} successfully loaded and processed.")

    def run_backtest(self, strategy):
        """Run the backtest using the provided strategy"""
        if self.data is None:
            raise ValueError("Market data not loaded.")

        for index, row in self.data.iterrows():
            signal = strategy.generate_signal(row)
            self.execute_trade(signal, row['Close'], index)

        results = self.evaluate_performance()
        self.update_metrics(results)
        return results

    def execute_trade(self, signal, price, date):
        """Execute buy/sell based on the strategy signal"""
        if signal == "BUY" and self.cash > price:
            self.positions += 1
            self.cash -= price * (1 + self.commission)
            self.trade_log.append((date, "BUY", price))
            backtest_logger.log("info", f"Buy executed: {price} on {date}")

        elif signal == "SELL" and self.positions > 0:
            self.positions -= 1
            self.cash += price * (1 - self.commission)
            self.trade_log.append((date, "SELL", price))
            backtest_logger.log("info", f"Sell executed: {price} on {date}")

    def evaluate_performance(self):
        """Evaluate backtest performance using metrics"""
        final_value = self.cash + (self.positions * self.data.iloc[-1]['Close'])
        metrics = PerformanceMetrics.evaluate_performance(self.trade_log, self.data)

        return {
            "final_capital": final_value,
            "return_percentage": (final_value / self.initial_cash - 1) * 100,
            "total_trades": len(self.trade_log),
            "profit_loss_ratio": self.calculate_profit_loss_ratio(),
            **metrics
        }

    def calculate_profit_loss_ratio(self):
        """Calculate profit/loss ratio"""
        profits = [trade[2] for trade in self.trade_log if trade[1] == "SELL"]
        losses = [trade[2] for trade in self.trade_log if trade[1] == "BUY"]
        return sum(profits) / sum(losses) if sum(losses) > 0 else 0

    def update_metrics(self, results):
        """Send performance metrics to Prometheus"""
        prometheus_url = "http://host.docker.internal:8001/update_metrics"
        payload = {
            "total_trades": results["total_trades"],
            "profit_loss_ratio": results["profit_loss_ratio"],
            "max_drawdown": results["max_drawdown"],
            "sharpe_ratio": results["sharpe_ratio"]
        }
        try:
            requests.post(prometheus_url, json=payload)
        except requests.exceptions.RequestException as e:
            backtest_logger.log("error", f"Error sending metrics to Prometheus: {e}")
