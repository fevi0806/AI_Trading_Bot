import zmq
import json
import logging
import threading
import requests
from pythonjsonlogger import jsonlogger

# Loki Logging Configuration
LOKI_URL = "http://localhost:3100/loki/api/v1/push"
logger = logging.getLogger("CommFramework")
logger.setLevel(logging.INFO)

logHandler = logging.StreamHandler()
formatter = jsonlogger.JsonFormatter()
logHandler.setFormatter(formatter)
logger.addHandler(logHandler)

class CommFramework:
    def __init__(self):
        self.context = zmq.Context()

        # PUB-SUB for Market Data Distribution
        self.market_pub_socket = self.context.socket(zmq.PUB)
        self.market_pub_socket.bind("tcp://127.0.0.1:5557")  # Market Data Broadcast

        # PUB-SUB for Trade Signals (Strategy -> Execution)
        self.signal_pub_socket = self.context.socket(zmq.PUB)
        self.signal_pub_socket.bind("tcp://127.0.0.1:5556")  # Trade Signal Publisher

        self.signal_sub_socket = self.context.socket(zmq.SUB)
        self.signal_sub_socket.connect("tcp://127.0.0.1:5556")  # Execution listens to this
        self.signal_sub_socket.setsockopt_string(zmq.SUBSCRIBE, "")

        # REP-REQ for Risk Management
        self.risk_socket = self.context.socket(zmq.REP)
        self.risk_socket.bind("tcp://127.0.0.1:5558")

        logger.info("✅ Communication Framework Initialized", extra={"service": "CommFramework"})

    def broadcast_market_data(self, data):
        """Publishes market data updates to all subscribers."""
        message = json.dumps(data)
        self.market_pub_socket.send_string(message)
        self.log_to_loki({"event": "Market Data Broadcast", "data": data})

    def send_trade_signal(self, signal):
        """Publishes trade signals for execution."""
        message = json.dumps(signal)
        self.signal_pub_socket.send_string(message)
        self.log_to_loki({"event": "Trade Signal Sent", "signal": signal})

    def listen_for_signals(self):
        """Execution Agent listens for trade signals."""
        while True:
            message = self.signal_sub_socket.recv_string()
            signal = json.loads(message)
            logger.info(f"📡 Received Trade Signal: {signal}", extra={"service": "CommFramework"})
            self.log_to_loki({"event": "Trade Signal Received", "signal": signal})

    def listen_for_risk_requests(self):
        """Handles risk assessment requests."""
        while True:
            request = self.risk_socket.recv_json()
            logger.info(f"🔎 Risk Check Requested: {request}", extra={"service": "CommFramework"})

            response = {"status": "approved", "response": f"Risk check OK for {request}"}
            self.risk_socket.send_json(response)
            self.log_to_loki({"event": "Risk Response Sent", "response": response})

    def log_to_loki(self, log_data):
        """Sends logs to Loki."""
        payload = {
            "streams": [
                {
                    "labels": "{service=\"CommFramework\"}",
                    "entries": [{"ts": json.dumps(log_data)}],
                }
            ]
        }
        requests.post(LOKI_URL, json=payload)

    def start(self):
        """Starts the communication framework."""
        threading.Thread(target=self.listen_for_signals, daemon=True).start()
        threading.Thread(target=self.listen_for_risk_requests, daemon=True).start()
        logger.info("🚀 CommFramework is now running.", extra={"service": "CommFramework"})

if __name__ == "__main__":
    comm = CommFramework()
    comm.start()
