import os
import time
import logging
import zmq
import pandas as pd

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

class ExecutionAgent:
    def __init__(self):
        logging.info("🚀 Execution Agent Initialized for Simulated Trading...")
       
        
        self.portfolio = {"SPY": 0, "QQQ": 0, "VGT": 0, "SOXX": 0, "ARKK": 0}
        self.cash_balance = 1_000_000  # Simulated starting capital

        # ZeroMQ setup
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.PULL)
        self.socket.bind("tcp://127.0.0.1:5560")
    
    def execute_trade(self, ticker, signal):
        """Executes trade in simulation mode."""
        if signal == "BUY":
            self.portfolio[ticker] += 100  # Buy 100 shares
            self.cash_balance -= 10_000  # Deduct cost (fixed for testing)
            logging.info(f"🟢 Simulated BUY: {ticker} | New Shares: {self.portfolio[ticker]}")
        elif signal == "SELL" and self.portfolio[ticker] > 0:
            self.portfolio[ticker] -= 100  # Sell 100 shares
            self.cash_balance += 10_000  # Add funds
            logging.info(f"🔴 Simulated SELL: {ticker} | Remaining Shares: {self.portfolio[ticker]}")
    
    def run(self):
        """Listens for trade signals and processes simulated trades."""
        while True:
            try:
                message = self.socket.recv_json()
                ticker = message.get("ticker")
                signal = message.get("signal")
                logging.info(f"📥 Received Trade Signal: {message}")
                self.execute_trade(ticker, signal)
            except Exception as e:
                logging.error(f"❌ Execution Error: {e}")
            time.sleep(1)

if __name__ == "__main__":
    agent = ExecutionAgent()
    agent.run()
