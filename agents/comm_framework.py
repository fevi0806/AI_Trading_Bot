import zmq
import logging
import yaml
import os
import psutil
import time

# Ensure Python can find the parent directory
import sys
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
        
        # Free occupied ports before starting
        self.free_ports()

    def load_config(self, config_path):
        """Load the configuration file for port assignments."""
        try:
            with open(config_path, "r") as file:
                config = yaml.safe_load(file)
            self.logger.info("✅ Configuration loaded successfully.")
            return config.get("ports", {})
        except Exception as e:
            self.logger.error(f"❌ Failed to load configuration: {e}")
            return {}

    def free_ports(self):
        """Finds and kills processes using required ports before binding."""
        for agent, ports in self.config.items():
            port = ports.get("publisher")
            if port:
                self._kill_process_using_port(port)

    def _kill_process_using_port(self, port):
        """Kill process occupying a given port."""
        for conn in psutil.net_connections():
            if conn.laddr.port == port:
                process = psutil.Process(conn.pid)
                self.logger.warning(f"🔴 Port {port} in use by process {process.name()} (PID {conn.pid}). Terminating...")
                process.terminate()
                time.sleep(1)
                self.logger.info(f"✅ Port {port} is now free.")

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
        except Exception as e:
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
        except Exception as e:
            self.logger.error(f"❌ Failed to connect subscriber for {agent_name} on port {port}: {e}")
            return None

    def cleanup(self):
        """Cleanup all ZeroMQ sockets on shutdown."""
        self.logger.info("🧹 Cleaning up ZeroMQ sockets...")
        
        for agent, socket in self.publishers.items():
            socket.close()
            self.logger.info(f"🔌 Closed publisher socket for {agent}")
        
        for agent, socket in self.subscribers.items():
            socket.close()
            self.logger.info(f"🔌 Closed subscriber socket for {agent}")

        self.context.term()
        self.logger.info("✅ ZeroMQ context terminated.")

