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
        self.running = True  # ✅ Enables graceful shutdown

        # ✅ Initialize communication sockets
        try:
            self.trade_sub = self.comm.create_subscriber("ExecutionAgent")
            self.execution_pub = self.comm.create_publisher("ExecutionAgent")
        except Exception as e:
            self.logger.error(f"❌ ExecutionAgent Init Error: {e}")
            self.trade_sub = None
            self.execution_pub = None

        if not self.trade_sub or not self.execution_pub:
            self.logger.error("❌ ExecutionAgent failed to initialize communication sockets.")
            return

    def execute_trade(self, signal):
        """Execute a trade based on the received signal."""
        ticker = signal.get("ticker", "Unknown")
        action = signal.get("signal", "Unknown")

        if action not in ["BUY", "SELL"]:
            self.logger.warning(f"⚠️ Invalid trade signal received: {action}")
            return

        self.logger.info(f"💼 Executing trade: {action} on {ticker}")

        # ✅ Simulate trade execution (Mock IBKR API Call)
        execution_feedback = {
            "ticker": ticker,
            "status": "executed",
            "action": action,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        }

        try:
            if self.execution_pub and not self.execution_pub.closed:
                self.execution_pub.send_json(execution_feedback)
                self.logger.info(f"📤 Execution feedback sent: {execution_feedback}")
            else:
                self.logger.warning("⚠️ Execution feedback not sent: Publisher socket is closed.")
        except Exception as e:
            self.logger.error(f"❌ Failed to send execution feedback: {e}")

    def run(self):
        """Continuously receive trade signals and execute trades."""
        self.logger.info("🚀 Execution Agent Started.")

        if not self.trade_sub:
            self.logger.error("❌ ExecutionAgent cannot start: No valid subscriber.")
            return

        while self.running:
            try:
                message = None
                try:
                    message = self.trade_sub.recv_string(flags=zmq.NOBLOCK)  # ✅ Non-blocking receive
                except zmq.Again:
                    pass  # ✅ No message available, continue looping

                if message:
                    signal = json.loads(message)
                    self.logger.info(f"📥 Received trade signal: {signal}")
                    self.execute_trade(signal)

            except Exception as e:
                self.logger.error(f"❌ Error processing trade signal: {e}")

            time.sleep(1)  # ✅ Prevent CPU overuse

    def stop(self):
        """Gracefully stops the ExecutionAgent."""
        self.logger.info("🛑 Stopping Execution Agent...")
        self.running = False  # ✅ Stops the loop properly
