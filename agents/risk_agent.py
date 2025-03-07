import zmq
import json
import logging

logging.basicConfig(level=logging.INFO)

class RiskManagementAgent:
    def __init__(self):
        self.context = zmq.Context()
        self.feedback_socket = self.context.socket(zmq.SUB)
        self.feedback_socket.connect("tcp://localhost:5559")
        self.feedback_socket.setsockopt_string(zmq.SUBSCRIBE, "")

        logging.info("✅ Risk Management Agent Initialized")

    def analyze_risk(self, execution_feedback):
        logging.info(f"🔍 Analyzing execution feedback: {execution_feedback}")

    def run(self):
        while True:
            message = self.feedback_socket.recv_string()
            execution_feedback = json.loads(message)
            logging.info(f"📥 Received Execution Feedback: {execution_feedback}")
            self.analyze_risk(execution_feedback)

if __name__ == "__main__":
    agent = RiskManagementAgent()
    agent.run()
