import numpy as np
import torch.optim as optim
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from models.rl_model import PPOModel
from utils.logger import setup_logger

class StrategyAgent:
    def __init__(self, comm_framework):  # Accept comm_framework as an argument
        self.logger = setup_logger()
        self.comm_framework = comm_framework  # Store comm_framework
        self.rl_model = PPOModel(input_dim=10, output_dim=3)  # Example: 10 features, 3 actions (BUY, SELL, HOLD)
        self.optimizer = optim.Adam(self.rl_model.parameters(), lr=0.001)  # Define the optimizer

    def generate_signal(self, state):
        """
        Generate a trade signal using the RL model.
        """
        action_probs, _ = self.rl_model(state)
        action = np.argmax(action_probs)  # Choose the action with the highest probability
        return action

    def update_model(self, state, action, reward):
        """
        Update the RL model based on the outcome of a trade.
        """
        action_probs, _ = self.rl_model(state)
        loss = -torch.log(action_probs[action]) * reward
        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()
        self.logger.info(f"Model updated with reward: {reward}")

    def start(self):
        self.logger.info("Strategy Agent started.")
        while True:
            state = np.random.rand(10)  # Replace with actual market data
            signal = self.generate_signal(state)
            self.logger.info(f"Generated signal: {signal}")

            # Simulate trade outcome (replace with actual outcome)
            reward = np.random.rand()
            self.update_model(state, signal, reward)