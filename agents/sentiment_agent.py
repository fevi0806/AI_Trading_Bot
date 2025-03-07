
import zmq
import json
import logging
import sys
import os

# Ensure Python can find the parent directory
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from agents.comm_framework import CommFramework  # ✅ Correct import path
venv_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".venv", "Lib", "site-packages"))
if venv_path not in sys.path:
    sys.path.insert(0, venv_path)

import zmq  # Now it should work!

from transformers import pipeline
from agents.comm_framework import CommFramework

logger = logging.getLogger(__name__)

class SentimentAgent:
    def __init__(self, comm_framework):
        """Initialize Sentiment Agent."""
        self.comm = comm_framework
        self.sub_socket = comm_framework.create_subscriber(5557, "NEWS")
        self.pub_socket = self.comm.create_publisher(5558)
        self.sentiment_pipeline = pipeline("sentiment-analysis", model="ProsusAI/finbert")

    def analyze_sentiment(self, news_text):
        """Analyzes sentiment using FinBERT."""
        result = self.sentiment_pipeline(news_text)
        return result[0]["label"]

    def run(self):
        """Continuously fetch and analyze news sentiment."""
        while True:
            try:
                topic, news_text = self.sub_socket.recv_string().split(" ", 1)
                sentiment = self.analyze_sentiment(news_text)
                self.pub_socket.send_string(f"NEWS {sentiment}")
                logger.info(f"Sentiment Analyzed: {sentiment} for News: {news_text[:50]}...")
            except Exception as e:
                logger.error(f"SentimentAgent Error: {e}")
