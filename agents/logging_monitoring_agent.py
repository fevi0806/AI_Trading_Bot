import zmq
import logging
import os
import sys
import time

# Ensure Python can find the parent directory
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from utils.logger import setup_logger
from agents.comm_framework import CommFramework

class LoggingMonitoringAgent:
    def __init__(self, comm_framework):
        """Initialize the Logging Monitoring Agent to collect logs from all agents."""
        self.comm = comm_framework
        self.logger = setup_logger("LoggingMonitoringAgent", "logs/logging_monitoring_agent.log")
        self.logger.info("📊 Logging Monitoring Agent Started and ready to receive logs.")
        self.subscribers = {}

        # Define agents to monitor
        self.agents = ["MarketDataAgent", "SentimentAgent", "StrategyAgent", "RiskManagementAgent", "ExecutionAgent"]

        # Subscribe to logs from all agents
        for agent in self.agents:
            try:
                self.subscribers[agent] = self.comm.create_subscriber(agent, topic="LOG")
                self.logger.info(f"✅ Subscribed to logs from {agent}")
            except Exception as e:
                self.logger.error(f"❌ Failed to subscribe to logs from {agent}: {e}")
                self.subscribers[agent] = None  # Mark as failed

    def run(self):
        """Continuously listen for logs from all agents."""
        self.logger.info("📊 Logging Monitoring Agent Started.")

        while True:
            for agent, subscriber in self.subscribers.items():
                if subscriber is None:
                    continue  # Skip if the subscription failed

                try:
                    if subscriber.poll(100):  # 100 ms timeout to prevent blocking
                        message = subscriber.recv_string()
                        self.logger.info(f"📝 {agent} Log: {message}")
                except zmq.ZMQError as e:
                    self.logger.error(f"❌ Error receiving log from {agent}: {e}")
                except Exception as e:
                    self.logger.error(f"❌ Unexpected error in LoggingMonitoringAgent for {agent}: {e}")

            time.sleep(1)
