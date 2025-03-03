import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from agents.market_data_agent import MarketDataAgent
from agents.strategy_agent import StrategyAgent
from agents.execution_agent import ExecutionAgent
from agents.risk_agent import RiskAgent
from agents.comm_framework import CommunicationFramework
from utils.logger import setup_logger

def main():
    # Set up logging
    logger = setup_logger()
    logger.info("Starting AI Trading Bot...")

    # Initialize communication framework
    comm_framework = CommunicationFramework()

    # Initialize agents
    market_data_agent = MarketDataAgent(comm_framework)
    strategy_agent = StrategyAgent(comm_framework)
    risk_agent = RiskAgent(comm_framework)
    execution_agent = ExecutionAgent(comm_framework)

    try:
        # Start the bot
        market_data_agent.start()
        strategy_agent.start()
        risk_agent.start()
        execution_agent.start()
    except KeyboardInterrupt:
        logger.info("AI Trading Bot stopped by user.")
    except Exception as e:
        logger.error(f"Error: {e}")

if __name__ == "__main__":
    main()