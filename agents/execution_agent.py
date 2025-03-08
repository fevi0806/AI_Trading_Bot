import zmq
import json
import time
import logging
import sys
import os

# Ensure Python can find the parent directory
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from agents.comm_framework import CommFramework  
from utils.logger import setup_logger

class ExecutionAgent:
    def __init__(self, comm_framework):
        self.comm = comm_framework
        self.logger = setup_logger("ExecutionAgent", "logs/execution_agent.log")

        # ✅ Load ports dynamically from config.yml
        self.trade_sub = self.comm.create_subscriber("ExecutionAgent")  # Uses the correct port from config
        self.execution_pub = self.comm.create_publisher("ExecutionAgent")  # Uses the correct port from config

        if not self.trade_sub or not self.execution_pub:
            self.logger.error("❌ ExecutionAgent failed to initialize communication sockets.")
            return

    def execute_trade(self, signal):
        """Execute a trade based on the received signal."""
        ticker = signal.get("ticker", "Unknown")
        action = signal.get("signal", "Unknown")

        self.logger.info(f"💼 Executing trade: {action} on {ticker}")

        # Placeholder for actual trade execution logic
        execution_feedback = {"ticker": ticker, "status": "executed", "action": action}

        try:
            self.execution_pub.send_json(execution_feedback)
            self.logger.info(f"📤 Execution feedback sent: {execution_feedback}")
        except Exception as e:
            self.logger.error(f"❌ Failed to send execution feedback: {e}")

    def run(self):
        """Continuously receive trade signals and execute trades."""
        self.logger.info("🚀 Execution Agent Started.")
        while True:
            try:
                if self.trade_sub.poll(100):  # 100ms timeout
                    message = self.trade_sub.recv_string()
                    signal = json.loads(message)
                    self.logger.info(f"📥 Received trade signal: {signal}")
                    self.execute_trade(signal)
            except Exception as e:
                self.logger.error(f"❌ Error processing trade signal: {e}")
            time.sleep(1)
