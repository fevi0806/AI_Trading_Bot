import logging

logging.basicConfig(level=logging.INFO)

def calculate_trade_reward(entry_price, exit_price, action):
    """Calculates reward based on trade performance."""
    profit = exit_price - entry_price
    reward = profit if action == "BUY" else -profit
    logging.info(f"💰 Trade Reward: {reward}")
    return reward

def log_trade_result(ticker, entry_price, exit_price, reward):
    """Logs trade results."""
    logging.info(f"📜 Trade Log: {ticker} | Entry: {entry_price} | Exit: {exit_price} | Reward: {reward}")
