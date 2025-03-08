import zmq
import json
import time
import logging
import sys
import os

# Ensure Python can find the parent directory
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from agents.comm_framework import CommFramework  # Adjusted import path
from utils.logger import setup_logger

class ExecutionAgent:
    def __init__(self, comm_framework):
        self.comm = comm_framework
        self.trade_sub = self.comm.create_subscriber(5558)  # Trade Signal Subscriber
        self.execution_pub = self.comm.create_publisher(5559)  # Execution Feedback Publisher
        self.logger = setup_logger("ExecutionAgent", "logs/execution_agent.log")

    def execute_trade(self, signal):
        ticker = signal["ticker"]
        action = signal["signal"]
        self.logger.info(f"💼 Executing trade: {action} on {ticker}")
        # Placeholder for actual trade execution logic
        execution_feedback = {"ticker": ticker, "status": "executed", "action": action}
        self.execution_pub.send_json(execution_feedback)
        self.logger.info(f"📤 Execution feedback sent: {execution_feedback}")

    def run(self):
        """Continuously receive trade signals and execute trades."""
        self.logger.info("🚀 Execution Agent Started.")
       

 
