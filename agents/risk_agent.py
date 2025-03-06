import zmq
import json
import logging

class RiskAgent:
    def __init__(self):
        self.context = zmq.Context()

        # Subscribe to Market Data
        self.sub_socket = self.context.socket(zmq.SUB)
        self.sub_socket.connect("tcp://localhost:5557")
        self.sub_socket.setsockopt_string(zmq.SUBSCRIBE, "")

        # Request-Reply Server for Risk Queries
        self.rep_socket = self.context.socket(zmq.REP)
        self.rep_socket.bind("tcp://*:5556")

        logging.info("Risk Agent connected to CommFramework.")

    def evaluate_trade_risk(self, ticker):
        """Dummy function returning a static risk score"""
        risk_data = {"ticker": ticker, "risk_score": 0.02}
        return risk_data

    def listen_for_requests(self):
        while True:
            request = self.rep_socket.recv_json()
            ticker = request.get("ticker")
            risk_data = self.evaluate_trade_risk(ticker)
            self.rep_socket.send_json(risk_data)

    def start(self):
        """Start RiskAgent: listen for risk requests and subscribe to market data."""
        self.listen_for_requests()

if __name__ == "__main__":
    agent = RiskAgent()
    agent.start()
