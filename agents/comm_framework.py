import zmq
import logging

class CommFramework:
    def __init__(self):
        """Initialize the communication framework with defined sockets."""
        self.context = zmq.Context()
        self.sockets = {}

        # Define communication endpoints
        self.endpoints = {
            "market_data_pub": 5555,
            "news_pub": 5556,
            "trade_signal_pub": 5557,
            "trade_feedback_pub": 5558,
            "logging_pub": 5559,
            "risk_feedback_sub": 5560
        }

        logging.info("✅ CommFramework Initialized")

    def create_publisher(self, port):
        """Creates and returns a publisher socket."""
        if port not in self.sockets:
            socket = self.context.socket(zmq.PUB)
            socket.bind(f"tcp://*:{port}")
            self.sockets[port] = socket
            logging.info(f"📡 Publisher bound on port {port}")
        return self.sockets[port]

    def create_subscriber(self, port, topic=""):
        """Creates and returns a subscriber socket."""
        if port not in self.sockets:
            socket = self.context.socket(zmq.SUB)
            socket.connect(f"tcp://localhost:{port}")
            socket.setsockopt_string(zmq.SUBSCRIBE, topic)
            self.sockets[port] = socket
            logging.info(f"🔍 Subscriber connected to port {port} with topic '{topic}'")
        return self.sockets[port]
