import numpy as np
import pandas as pd
import gymnasium as gym
from gymnasium import spaces
from stable_baselines3 import PPO
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

class TradingEnv(gym.Env):
    """Custom Trading Environment for Reinforcement Learning"""
    def __init__(self, ticker, lookback=50, initial_balance=10000):
        super(TradingEnv, self).__init__()

        self.ticker = ticker
        self.lookback = lookback
        self.initial_balance = initial_balance
        self.balance = initial_balance
        self.position = 0
        self.current_step = 0

        # Load market data
        self.df = pd.read_csv(f"data/{ticker}_processed.csv", index_col=0)

        # ✅ Fix NaN issues in data
        self.df.fillna(method="ffill", inplace=True)  # Forward-fill missing values
        self.df.fillna(method="bfill", inplace=True)  # Backward-fill remaining NaN

        self.num_steps = len(self.df) - self.lookback
        logging.info(f"✅ Loaded {len(self.df)} rows for {ticker}.")

        # Define action and observation spaces
        self.action_space = spaces.Discrete(3)  # 0 = Hold, 1 = Buy, 2 = Sell
        self.observation_space = spaces.Box(low=-np.inf, high=np.inf, shape=(lookback, 3), dtype=np.float32)

    def reset(self, seed=None, options=None):
        """Resets environment at the beginning of each episode"""
        self.balance = self.initial_balance
        self.position = 0
        self.current_step = 0
        return self._get_observation(), {}

    def step(self, action):
        """Takes an action and returns the next state, reward, and termination signal"""
        done = False
        current_price = self.df.iloc[self.current_step]["Adj Close"]

        # ✅ Fix: Ensure price is not NaN or Zero (Prevent divide by zero)
        if np.isnan(current_price) or current_price == 0:
            logging.warning(f"❌ Invalid price detected at step {self.current_step}, setting price to $1.")
            current_price = 1  # Set minimum price to avoid errors

        reward = 0

        if action == 1:  # Buy
            if self.balance > 0:  # ✅ Fix: Only buy if there's balance
                self.position = self.balance / current_price
                self.balance = 0
        elif action == 2 and self.position > 0:  # Sell
            self.balance = self.position * current_price
            reward = self.balance - self.initial_balance  # ✅ Ensure valid reward
            reward = np.clip(reward, -10000, 10000)  # ✅ Prevent extreme reward values
            self.position = 0

        # ✅ Fix: Prevent NaN rewards
        if not np.isfinite(reward):
            logging.error(f"❌ NaN/Inf detected in reward at step {self.current_step}, setting reward to 0.")
            reward = 0

        # Move to the next step
        self.current_step += 1
        if self.current_step >= self.num_steps:
            done = True

        return self._get_observation(), reward, done, False, {}

    def _get_observation(self):
        """Returns the most recent price & volume data, ensuring no NaN values"""
        obs = self.df.iloc[self.current_step:self.current_step + self.lookback].values
        obs = np.nan_to_num(obs)  # ✅ Convert NaNs to 0
        obs = np.clip(obs, -1e6, 1e6)  # ✅ Prevent extreme values

        # ✅ Debugging Step: Log any invalid observations
        if not np.isfinite(obs).all():
            logging.error(f"❌ NaN or Inf detected in observation at step {self.current_step} for {self.ticker}")
            obs = np.zeros_like(obs)  # Replace invalid observation with zeros

        return obs

def train_ppo(ticker, timesteps=100000):
    """Trains PPO on the trading environment, ensuring valid inputs"""
    env = TradingEnv(ticker)

    # ✅ Add validation step before training
    test_obs, _ = env.reset()
    if not np.isfinite(test_obs).all():
        logging.error(f"❌ NaN or Inf found in initial observation for {ticker}!")
        return

    logging.info(f"✅ Training PPO model for {ticker} with {timesteps} timesteps...")

    model = PPO("MlpPolicy", env, learning_rate=0.0003, verbose=1)
    model.learn(total_timesteps=timesteps)

    model_path = f"models/{ticker}_ppo"
    model.save(model_path)
    
    if os.path.exists(model_path):
        logging.info(f"✅ PPO model saved for {ticker} at {model_path}")
    else:
        logging.error(f"❌ PPO model NOT saved for {ticker}!")

if __name__ == "__main__":
    tickers = ["QQQ", "VGT", "SOXX", "ARKK", "SPY"]
    os.makedirs("models/", exist_ok=True)

    for ticker in tickers:
        train_ppo(ticker)

    logging.info("✅ All PPO models trained successfully!")
