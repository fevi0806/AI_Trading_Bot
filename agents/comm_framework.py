import zmq

class CommunicationFramework:
    def __init__(self):
        self.context = zmq.Context()

        # Create sockets
        self.market_data_socket = self.context.socket(zmq.PUB)
        self.strategy_socket = self.context.socket(zmq.SUB)
        self.risk_socket = self.context.socket(zmq.PUSH)
        self.execution_socket = self.context.socket(zmq.PULL)

        # Bind sockets
        self.market_data_socket.bind("tcp://*:5555")
        self.strategy_socket.bind("tcp://*:5556")
        self.risk_socket.bind("tcp://*:5557")
        self.execution_socket.bind("tcp://*:5558")

    def send_market_data(self, data):
        """
        Send market data as JSON.
        """
        self.market_data_socket.send_json(data)