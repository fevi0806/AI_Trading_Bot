import zmq
import json
import time
import logging
import random  # Simulating order execution results

# Logging Configuration
logging.basicConfig(level=logging.INFO)

# Risk Management Parameters
MAX_TRADES_PER_HOUR = 5  # Limit the number of trades per hour
STOP_LOSS_PERCENTAGE = 0.02  # 2% Stop-Loss
TAKE_PROFIT_PERCENTAGE = 0.05  # 5% Take-Profit

class ExecutionAgent:
    def __init__(self, comm_framework):
        self.trade_socket = comm_framework.create_subscriber(5559)  # Risk-validated trades

        # Subscribe to Trade Signals (from Strategy Agent)
        self.trade_socket = self.context.socket(zmq.SUB)
        self.trade_socket.connect("tcp://localhost:5557")
        self.trade_socket.setsockopt_string(zmq.SUBSCRIBE, "")

        # Publish Trade Feedback (to Strategy Agent)
        self.feedback_socket = self.context.socket(zmq.PUB)
        self.feedback_socket.connect("tcp://localhost:5558")

        self.trade_history = []  # Store executed trades for risk control
        logging.info("✅ Execution Agent Initialized")

    def validate_trade(self, ticker, action, current_price):
        """Ensures trade follows risk management rules."""
        if action == "HOLD":
            return False, "Holding position - No trade needed."

        # Check trading frequency
        recent_trades = [t for t in self.trade_history if t["time"] > time.time() - 3600]
        if len(recent_trades) >= MAX_TRADES_PER_HOUR:
            return False, "Trade limit reached for this hour."

        # Define Stop-Loss and Take-Profit
        stop_loss = round(current_price * (1 - STOP_LOSS_PERCENTAGE), 2)
        take_profit = round(current_price * (1 + TAKE_PROFIT_PERCENTAGE), 2)

        return True, {"stop_loss": stop_loss, "take_profit": take_profit}

    def execute_trade(self, signal):
        """Executes trade based on received signal."""
        ticker = signal["ticker"]
        action = signal["signal"]
        current_price = signal.get("price", random.uniform(100, 500))  # Simulated price

        valid, trade_data = self.validate_trade(ticker, action, current_price)
        if not valid:
            logging.warning(f"🚫 Trade Rejected: {trade_data}")
            return

        # Simulate trade execution
        execution_status = random.choice(["success", "failed"])
        trade_result = {
            "ticker": ticker,
            "status": execution_status,
            "action": action,
            "price": current_price,
            "stop_loss": trade_data["stop_loss"],
            "take_profit": trade_data["take_profit"],
            "time": time.time()
        }

        if execution_status == "success":
            self.trade_history.append(trade_result)

        # Log the trade
        logging.info(f"🚀 Trade Executed: {trade_result}")

        # Send feedback to Strategy Agent
        self.feedback_socket.send_string(json.dumps(trade_result))

    def run(self):
        """Main execution loop."""
        while True:
            message = self.trade_socket.recv_string()
            signal = json.loads(message)
            logging.info(f"📥 Received Trade Signal: {signal}")
            self.execute_trade(signal)
            time.sleep(2)

if __name__ == "__main__":
    agent = ExecutionAgent()
    agent.run()
