import zmq
import json
import time
import logging

logging.basicConfig(level=logging.INFO)

class ExecutionAgent:
    def __init__(self):
        self.context = zmq.Context()

        # SUB socket to receive trade signals
        self.trade_socket = self.context.socket(zmq.SUB)
        self.trade_socket.connect("tcp://localhost:5557")
        self.trade_socket.setsockopt_string(zmq.SUBSCRIBE, "")

        # PUB socket to send execution feedback
        self.feedback_socket = self.context.socket(zmq.PUB)
        self.feedback_socket.connect("tcp://localhost:5559")

        logging.info("✅ Execution Agent Initialized")

    def execute_trade(self, signal):
        """Simulates trade execution."""
        ticker = signal["ticker"]
        action = signal["signal"]
        logging.info(f"🚀 Executing trade: {action} on {ticker}")

        execution_feedback = {"ticker": ticker, "status": "executed", "action": action}
        self.feedback_socket.send_string(json.dumps(execution_feedback))

    def run(self):
        """Main loop to listen for trade signals and execute trades."""
        while True:
            message = self.trade_socket.recv_string()
            signal = json.loads(message)
            logging.info(f"📥 Received Trade Signal: {signal}")
            self.execute_trade(signal)
            time.sleep(2)

if __name__ == "__main__":
    agent = ExecutionAgent()
    agent.run()
