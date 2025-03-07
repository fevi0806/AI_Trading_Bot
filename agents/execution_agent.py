import zmq
import json
import time
import logging
import sys
import os

# Ensure Python can find the parent directory
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from agents.comm_framework import CommFramework  # ✅ Correct import path

logging.basicConfig(level=logging.INFO)

class ExecutionAgent:
    def __init__(self, comm_framework):
        self.comm = comm_framework
        self.context = zmq.Context()

        self.trade_sub = self.context.socket(zmq.SUB)
        self.trade_sub.connect("tcp://localhost:5557")
        self.trade_sub.setsockopt_string(zmq.SUBSCRIBE, "")

        self.execution_pub = self.context.socket(zmq.PUB)
        self.execution_pub.connect("tcp://localhost:5559")

        logging.info("✅ Execution Agent Initialized")

    def execute_trade(self, signal):
        ticker = signal["ticker"]
        action = signal["signal"]

        logging.info(f"🚀 Executing trade: {action} on {ticker}")

        execution_feedback = {"ticker": ticker, "status": "executed", "action": action}
        self.execution_pub.send_json(execution_feedback)

    def run(self):
        while True:
            message = self.trade_sub.recv_json()
            self.execute_trade(message)
            time.sleep(2)

if __name__ == "__main__":
    comm_framework = CommFramework()
    agent = ExecutionAgent(comm_framework)
    agent.run()
