import threading
import logging
import sys
import os

# Ensure Python can find the parent directory
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from agents.comm_framework import CommFramework
from agents.market_data_agent import MarketDataAgent
from agents.sentiment_agent import SentimentAgent
from agents.strategy_agent import StrategyAgent
from agents.risk_agent import RiskManagementAgent
from agents.execution_agent import ExecutionAgent
from agents.logging_monitoring_agent import LoggingMonitoringAgent

logging.basicConfig(level=logging.INFO)

comm_framework = CommFramework()

AGENTS = {
    "MarketDataAgent": MarketDataAgent,
    "SentimentAgent": SentimentAgent,
    "StrategyAgent": StrategyAgent,
    "RiskAgent": RiskManagementAgent,
    "ExecutionAgent": ExecutionAgent,
    "LoggingMonitoringAgent": LoggingMonitoringAgent
}

def start_agent(agent_class, name):
    try:
        agent = agent_class(comm_framework)
        agent.run()
        logging.info(f"{name} started successfully.")
    except Exception as e:
        logging.error(f"Failed to start {name}: {e}")

if __name__ == "__main__":
    threads = []
    for agent_name, agent_class in AGENTS.items():
        thread = threading.Thread(target=start_agent, args=(agent_class, agent_name))
        thread.start()
        threads.append(thread)

    for thread in threads:
        thread.join()
