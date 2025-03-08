import zmq
import json
import logging
import sys
import os

# Ensure Python can find the parent directory
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from agents.comm_framework import CommFramework  # ✅ Correct import path
logging.basicConfig(level=logging.INFO)

class RiskManagementAgent:
    def __init__(self, comm_framework):
        self.comm = comm_framework
        self.context = zmq.Context()

        self.risk_socket = self.context.socket(zmq.REP)
        self.risk_socket.connect("tcp://localhost:5558")

        self.execution_sub = self.context.socket(zmq.SUB)
        self.execution_sub.connect("tcp://localhost:5559")
        self.execution_sub.setsockopt_string(zmq.SUBSCRIBE, "")

        logging.info("🛡️ Risk Management Agent Initialized")

    def assess_risk(self, ticker, action):
        """Evaluates if a trade should be executed."""
        if action == "BUY":
            return {"approved": True, "reason": "Low risk detected"}
        elif action == "SELL":
            return {"approved": True, "reason": "Selling condition met"}
        return {"approved": False, "reason": "Default HOLD"}

    def listen_for_risk_requests(self):
        """Handles risk validation requests from Strategy Agent."""
        while True:
            request = self.risk_socket.recv_json()
            ticker, action = request["ticker"], request["action"]
            response = self.assess_risk(ticker, action)
            self.risk_socket.send_json(response)

    def monitor_executions(self):
        """Monitors trade executions from Execution Agent."""
        while True:
            message = self.execution_sub.recv_json()
            logging.info(f"📊 Execution Feedback: {message}")

    def run(self):
        logging.info("🛡️ Risk Management Agent Running")
        self.listen_for_risk_requests()

if __name__ == "__main__":
    comm_framework = CommFramework()
    agent = RiskManagementAgent(comm_framework)
    agent.run()
