import logging
import os

def setup_logger():
    """
    Set up a centralized logger.
    """
    # Create logs directory if it doesn't exist
    if not os.path.exists("logs"):
        os.makedirs("logs")

    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler("logs/ai_trading_bot.log"),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)