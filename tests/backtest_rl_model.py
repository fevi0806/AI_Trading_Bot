import pandas as pd
import gym
from stable_baselines3 import PPO

class TradingEnv(gym.Env):
    def __init__(self, stock_data):
        super(TradingEnv, self).__init__()
        self.stock_data = stock_data
        self.current_step = 0

    def step(self, action):
        reward = self._calculate_reward(action)
        self.current_step += 1
        done = self.current_step >= len(self.stock_data) - 1
        return self.stock_data.iloc[self.current_step], reward, done, {}

    def reset(self):
        self.current_step = 0
        return self.stock_data.iloc[self.current_step]

def train_rl_model(stock_data):
    env = TradingEnv(stock_data)
    model = PPO("MlpPolicy", env, verbose=1)
    model.learn(total_timesteps=10000)
    return model
