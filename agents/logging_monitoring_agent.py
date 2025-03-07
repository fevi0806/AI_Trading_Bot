import zmq
import logging
import sys
import os

# Ensure Python can find the parent directory
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from agents.comm_framework import CommFramework  # ✅ Correct import path
from utils.logger import setup_logger

# Set up logging
setup_logger()
logger = logging.getLogger(__name__)

class LoggingMonitoringAgent:
    def __init__(self, comm_framework):
        self.sub_socket = comm_framework.create_subscriber(5560)  # Log messages

    def run(self):
        """Continuously collect logs from agents and send to Loki."""
        while True:
            try:
                log_message = self.sub_socket.recv_string()
                self.log_storage.append(log_message)
                logger.info(f"Log Collected: {log_message}")
            except Exception as e:
                logger.error(f"LoggingMonitoringAgent Error: {e}")
