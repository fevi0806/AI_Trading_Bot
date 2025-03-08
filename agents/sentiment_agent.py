import zmq
import json
import time
import logging
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from utils.logger import setup_logger
from agents.comm_framework import CommFramework

class SentimentAgent:
    def __init__(self, comm_framework):
        self.comm = comm_framework
        self.publisher = self.comm.create_publisher("SentimentAgent")
        self.subscriber = self.comm.create_subscriber("SentimentAgent", topic="NEWS")
        self.logger = setup_logger("SentimentAgent", "logs/sentiment_agent.log")

    def run(self):
        self.logger.info("🚀 Sentiment Agent Started.")
        while True:
            try:
                message = self.subscriber.recv_string()
                self.logger.info(f"📥 Received News Data: {message}")

                # Process sentiment analysis (Placeholder logic)
                sentiment = "Positive"  # Dummy sentiment

                sentiment_data = {"sentiment": sentiment}
                self.comm.send_message("SentimentAgent", json.dumps(sentiment_data))
                self.logger.info(f"📤 Sentiment Sent: {sentiment_data}")

            except Exception as e:
                self.logger.error(f"❌ Error in SentimentAgent loop: {e}")
            time.sleep(60)
