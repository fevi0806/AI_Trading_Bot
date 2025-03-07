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
        """Initializes the ZeroMQ communication framework."""
        self.context = zmq.Context()

        # Trade Signal Publisher (For Strategy → Execution)
        self.trade_signal_pub = self.create_publisher(5557)

        # Market Data Publisher (For Market Data → Strategy & Sentiment)
        self.market_data_pub = self.create_publisher(5555)

        # Sentiment Data Publisher (For Sentiment → Strategy)
        self.sentiment_data_pub = self.create_publisher(5556)

        # Execution Feedback Publisher (For Execution → Risk & Strategy)
        self.execution_feedback_pub = self.create_publisher(5559)

        # Log Subscriber (For Logging & Monitoring)
        self.log_sub = self.create_subscriber(5560)

        # Request-Reply for direct agent communication
        self.rep_socket = self.context.socket(zmq.REP)
        self.rep_socket.bind("tcp://*:5561")

        logger.info("✅ CommFramework Initialized")

    def create_publisher(self, port):
        """Creates and binds a ZMQ publisher socket."""
        socket = self.context.socket(zmq.PUB)
        socket.bind(f"tcp://*:{port}")
        logger.info(f"📡 Publisher bound on port {port}")
        return socket

    def create_subscriber(self, port, topic=""):
        """Creates and connects a ZMQ subscriber socket."""
        socket = self.context.socket(zmq.SUB)
        socket.connect(f"tcp://localhost:{port}")
        socket.setsockopt_string(zmq.SUBSCRIBE, topic)
        logger.info(f"🔍 Subscriber connected to port {port} with topic '{topic}'")
        return socket

    def listen_for_requests(self):
        """Handles agent requests (e.g., risk assessments, trade execution feedback)."""
        while True:
            request = self.rep_socket.recv_json()
            logger.info(f"📥 Received request: {request}")

            response = {"status": "success", "response": f"Processed {request}"}
            self.rep_socket.send_json(response)
            self.log_to_loki({"event": "Processed Agent Request", "request": request})

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
        try:
            requests.post(LOKI_URL, json=payload)
        except requests.RequestException as e:
            logger.error(f"❌ Failed to send log to Loki: {e}")

    def start(self):
        """Starts the communication framework."""
        threading.Thread(target=self.listen_for_requests, daemon=True).start()
        logger.info("🚀 CommFramework is now running!")

if __name__ == "__main__":
    comm = CommFramework()
    comm.start()
