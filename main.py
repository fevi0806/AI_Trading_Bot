import threading
import logging
import sys
import os
import signal
import atexit
import time

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from agents.comm_framework import CommFramework
from agents.market_data_agent import MarketDataAgent
from agents.sentiment_agent import SentimentAgent
from agents.strategy_agent import StrategyAgent
from agents.risk_agent import RiskManagementAgent
from agents.execution_agent import ExecutionAgent
from agents.logging_monitoring_agent import LoggingMonitoringAgent

# Configure logging (Global Logger)
logging.basicConfig(level=logging.INFO)

# Initialize communication framework
comm_framework = CommFramework()

# Dictionary of agent names and their classes
AGENTS = {
    "MarketDataAgent": MarketDataAgent,
    "SentimentAgent": SentimentAgent,
    "StrategyAgent": StrategyAgent,
    "RiskManagementAgent": RiskManagementAgent,
    "ExecutionAgent": ExecutionAgent,
    "LoggingMonitoringAgent": LoggingMonitoringAgent
}

# Track running agent threads
threads = []
running_agents = []
shutdown_flag = False  # Global flag to control shutdown

# Graceful shutdown function
def shutdown(signum=None, frame=None):
    """Handles termination signals and cleans up resources."""
    global shutdown_flag
    shutdown_flag = True
    logging.info(f"🚨 Received termination signal ({signum}). Shutting down agents...")

    # Stop all agents safely
    for agent in running_agents:
        try:
            logging.info(f"🛑 Stopping {agent.__class__.__name__}...")
            agent.running = False  # Signal agents to stop their loops
        except Exception as e:
            logging.error(f"❌ Error stopping {agent.__class__.__name__}: {e}")

    time.sleep(2)  # Give agents time to clean up

    # Cleanup ZeroMQ sockets properly
    try:
        comm_framework.cleanup()
        logging.info("🧹 ZeroMQ sockets cleaned up.")
    except Exception as e:
        logging.error(f"❌ Error cleaning up ZeroMQ sockets: {e}")

    # ✅ Close logging handlers to prevent file I/O errors
    logging.shutdown()

    # Exit safely
    sys.exit(0)

# Ensure cleanup on exit
atexit.register(shutdown)
signal.signal(signal.SIGINT, shutdown)
signal.signal(signal.SIGTERM, shutdown)

def start_agent(agent_class, name):
    """Starts an agent and adds it to the running agents list."""
    try:
        agent = agent_class(comm_framework)
        agent.running = True  # Ensure each agent has a running flag
        running_agents.append(agent)
        agent.run()
        logging.info(f"✅ {name} started successfully.")
    except Exception as e:
        logging.error(f"❌ Failed to start {name}: {e}")

if __name__ == "__main__":
    logging.info("🚀 Starting all agents...")

    # Start all agents in separate threads
    for agent_name, agent_class in AGENTS.items():
        thread = threading.Thread(target=start_agent, args=(agent_class, agent_name), daemon=True)
        thread.start()
        threads.append(thread)

    # Keep main thread alive while agents run
    try:
        while not shutdown_flag:
            time.sleep(1)
    except KeyboardInterrupt:
        logging.info("🛑 Manual interruption detected.")
        shutdown()
