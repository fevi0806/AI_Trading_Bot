import zmq
import logging
import yaml
import os
import sys

# Ensure Python can find the parent directory
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from utils.logger import setup_logger

class CommFramework:
    def __init__(self, config_path="config/config.yml"):
        """Initialize the communication framework with ZeroMQ context."""
        self.context = zmq.Context()
        self.publishers = {}
        self.subscribers = {}
        self.logger = setup_logger("CommFramework", "logs/comm_framework.log")
        self.config = self.load_config(config_path)

    def load_config(self, config_path):
        """Load the configuration file for port assignments."""
        if not os.path.exists(config_path):
            self.logger.error(f"❌ Config file not found: {config_path}")
            return {}

        try:
            with open(config_path, "r") as file:
                config = yaml.safe_load(file)
            self.logger.info("✅ Configuration loaded successfully.")
            return config.get("ports", {})
        except Exception as e:
            self.logger.error(f"❌ Failed to load configuration: {e}")
            return {}

    def create_publisher(self, agent_name):
        """Create and bind a publisher socket for a given agent."""
        if agent_name not in self.config:
            self.logger.error(f"❌ No port assigned for {agent_name} in config.")
            return None
        
        port = self.config[agent_name].get("publisher")
        if not port:
            self.logger.error(f"❌ Publisher port missing for {agent_name}.")
            return None

        try:
            socket = self.context.socket(zmq.PUB)
            socket.bind(f"tcp://*:{port}")
            self.publishers[agent_name] = socket
            self.logger.info(f"📡 {agent_name} Publisher bound on port {port}")
            return socket
        except zmq.ZMQError as e:
            self.logger.error(f"❌ Failed to bind publisher for {agent_name} on port {port}: {e}")
            return None

    def create_subscriber(self, agent_name, topic=""):
        """Create and connect a subscriber socket for a given agent."""
        if agent_name not in self.config:
            self.logger.error(f"❌ No port assigned for {agent_name} in config.")
            return None

        port = self.config[agent_name].get("subscriber")
        if not port:
            self.logger.error(f"❌ Subscriber port missing for {agent_name}.")
            return None

        try:
            socket = self.context.socket(zmq.SUB)
            socket.connect(f"tcp://localhost:{port}")
            socket.setsockopt_string(zmq.SUBSCRIBE, topic)
            self.subscribers[agent_name] = socket
            self.logger.info(f"🔍 {agent_name} Subscriber connected to port {port} with topic '{topic}'")
            return socket
        except zmq.ZMQError as e:
            self.logger.error(f"❌ Failed to connect subscriber for {agent_name} on port {port}: {e}")
            return None

    def send_message(self, agent_name, message):
        """Send a message from a publisher."""
        if agent_name not in self.publishers:
            self.logger.error(f"❌ No publisher registered for {agent_name}.")
            return

        try:
            self.publishers[agent_name].send_string(message)
            self.logger.info(f"📤 {agent_name} sent message: {message}")
        except zmq.ZMQError as e:
            self.logger.error(f"❌ Failed to send message from {agent_name}: {e}")

    def receive_message(self, agent_name):
        """Receive a message for a subscriber."""
        if agent_name not in self.subscribers:
            self.logger.error(f"❌ No subscriber registered for {agent_name}.")
            return None

        try:
            message = self.subscribers[agent_name].recv_string()
            self.logger.info(f"📥 {agent_name} received message: {message}")
            return message
        except zmq.ZMQError as e:
            self.logger.error(f"❌ Failed to receive message for {agent_name}: {e}")
            return None
