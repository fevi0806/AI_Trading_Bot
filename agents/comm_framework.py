import zmq
import json
import threading
import logging

logging.basicConfig(level=logging.INFO)

class CommFramework:
    def __init__(self):
        self.context = zmq.Context()

        # PUB-SUB for trade signals
        self.trade_pub = self.context.socket(zmq.PUB)
        self.trade_pub.bind("tcp://*:5557")

        # PUB-SUB for execution feedback
        self.execution_pub = self.context.socket(zmq.PUB)
        self.execution_pub.bind("tcp://*:5559")

        # REQ-REP for risk agent
        self.risk_rep = self.context.socket(zmq.REP)
        self.risk_rep.bind("tcp://*:5561")

        # REQ-REP for sentiment agent
        self.sentiment_rep = self.context.socket(zmq.REP)
        self.sentiment_rep.bind("tcp://*:5563")

        logging.info("✅ CommFramework Initialized")

    def start(self):
        """Starts listening for incoming requests."""
        threading.Thread(target=self.listen_for_risk, daemon=True).start()
        threading.Thread(target=self.listen_for_sentiment, daemon=True).start()
        logging.info("✅ CommFramework Running...")

    def listen_for_risk(self):
        """Listens for risk assessment requests."""
        while True:
            request = self.risk_rep.recv_json()
            logging.info(f"📡 Risk Assessment Request: {request}")
            response = {"status": "approved", "risk_level": "low"}
            self.risk_rep.send_json(response)

    def listen_for_sentiment(self):
        """Listens for sentiment analysis requests."""
        while True:
            request = self.sentiment_rep.recv_json()
            logging.info(f"📰 Sentiment Analysis Request: {request}")
            response = {"status": "processed", "sentiment_score": 0.75}
            self.sentiment_rep.send_json(response)

if __name__ == "__main__":
    comm = CommFramework()
    comm.start()
