from utils.logger import setup_logger

class RiskAgent:
    def __init__(self, comm_framework):  # Accept comm_framework as an argument
        self.logger = setup_logger()
        self.comm_framework = comm_framework  # Store comm_framework

    def calculate_position_size(self, portfolio_value=100000, risk_per_trade=0.01):
        """
        Calculate the position size based on risk tolerance.
        """
        return portfolio_value * risk_per_trade

    def start(self):
        self.logger.info("Risk Agent started.")
        while True:
            position_size = self.calculate_position_size()
            self.logger.info(f"Calculated position size: {position_size}")
            self.comm_framework.send_risk_assessment({"position_size": position_size})  # Send risk assessment