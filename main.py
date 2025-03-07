import threading
import logging
import os
import tensorflow as tf

# Suppress TensorFlow logs
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
tf.get_logger().setLevel('ERROR')
TF_ENABLE_ONEDNN_OPTS=0
import sys

# Ensure Python can find all modules
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from agents.comm_framework import CommFramework
from agents.market_data_agent import MarketDataAgent
from agents.sentiment_agent import SentimentAgent
from agents.strategy_agent_2 import StrategyAgent
from agents.risk_agent import RiskAgent
from agents.execution_agent import ExecutionAgent
from agents.logging_monitoring_agent import LoggingMonitoringAgent
import threading
import logging

# Initialize CommFramework instance
comm_framework = CommFramework()

# Dictionary now stores **classes**, not instances
AGENTS = {
    "MarketDataAgent": MarketDataAgent,
    "SentimentAgent": SentimentAgent,
    "StrategyAgent": StrategyAgent,
    "RiskAgent": RiskAgent,
    "ExecutionAgent": ExecutionAgent,
    "LoggingMonitoringAgent": LoggingMonitoringAgent
}

def start_agent(agent_class, name):
    """Start an agent in a separate thread."""
    try:
        agent = agent_class(comm_framework)  # ✅ Now we create an instance here
        agent.run()
        logging.info(f"{name} started successfully.")
    except Exception as e:
        logging.error(f"Failed to start {name}: {e}")

if __name__ == "__main__":
    threads = []

    # Start all agents in parallel
    for agent_name, agent_class in AGENTS.items():
        thread = threading.Thread(target=start_agent, args=(agent_class, agent_name))
        thread.start()
        threads.append(thread)

    # Keep the main script running
    for thread in threads:
        thread.join()
