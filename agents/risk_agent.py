import zmq
import json
import logging

logging.basicConfig(level=logging.INFO)

class RiskManagementAgent:
    def __init__(self, comm_framework):
        self.sub_socket = comm_framework.create_subscriber(5558)  # Strategy signals
        self.pub_socket = comm_framework.create_publisher(5559)  # Send risk-approved orders

    def assess_risk(self, signal):
        # Dummy risk logic: Allow all trades
        return signal

    def run(self):
        while True:
            message = self.sub_socket.recv_string()
            trade_signal = json.loads(message)
            risk_checked_signal = self.assess_risk(trade_signal)
            self.pub_socket.send_string(json.dumps(risk_checked_signal))
            logging.info(f"📊 Risk Management Approved: {risk_checked_signal}")

if __name__ == "__main__":
    agent = RiskManagementAgent()
    agent.run()
