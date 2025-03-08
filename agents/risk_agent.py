import zmq
import json
import time
import logging
import os
import sys

# Ensure Python can find the parent directory
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from utils.logger import setup_logger
from agents.comm_framework import CommFramework

class RiskManagementAgent:
    def __init__(self, comm_framework):
        """Initialize the Risk Management Agent with communication framework."""
        self.comm = comm_framework
        self.logger = setup_logger("RiskManagementAgent", "logs/risk_management.log")

        try:
            self.subscriber = self.comm.create_subscriber("RiskManagementAgent")
            self.publisher = self.comm.create_publisher("RiskManagementAgent")
        except Exception as e:
            self.subscriber = None
            self.publisher = None
            self.logger.error(f"❌ RiskManagementAgent Subscriber/Publisher Init Error: {e}")

    def evaluate_risk(self, trade_signal):
        """Evaluate the risk of a given trade signal."""
        self.logger.info(f"🔍 Evaluating Trade Signal: {trade_signal}")

        # Placeholder Risk Evaluation Logic
        risk_assessment = {"status": "Approved", "details": "No risk detected"}

        return risk_assessment

    def run(self):
        """Continuously listen for trade signals and process risk assessment."""
        self.logger.info("🛡️ Risk Management Agent Started.")

        if not self.subscriber or not self.publisher:
            self.logger.error("❌ RiskManagementAgent failed to initialize communication sockets.")
            return

        while True:
            try:
                if self.subscriber.poll(500):  # Timeout after 500ms
                    message = self.subscriber.recv_string()
                    trade_signal = json.loads(message)
                    self.logger.info(f"📥 Received Trade Signal: {trade_signal}")

                    # Evaluate the risk of the trade
                    risk_result = self.evaluate_risk(trade_signal)

                    # Send the risk assessment result
                    response = {
                        "ticker": trade_signal.get("ticker", "Unknown"),
                        "signal": trade_signal.get("signal", "Unknown"),
                        "risk_status": risk_result["status"],
                        "details": risk_result["details"],
                    }

                    self.comm.send_message("RiskManagementAgent", json.dumps(response))
                    self.logger.info(f"🛡️ Risk Evaluation Sent: {response}")

                else:
                    self.logger.debug("🔄 No new messages in RiskManagementAgent.")

            except Exception as e:
                self.logger.error(f"❌ Error in RiskManagementAgent: {e}")
            time.sleep(1)
