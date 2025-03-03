import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.contract import Contract
from ibapi.order import Order
from agents.comm_framework import CommunicationFramework  # Correct import path
from utils.logger import setup_logger
import threading
import time

class ExecutionAgent(EClient, EWrapper):
    def __init__(self, comm_framework):
        EClient.__init__(self, self)
        self.comm_framework = comm_framework
        self.order_id = 1  # Unique order ID
        self.next_valid_order_id = None

    def start(self):
        # Connect to IBKR TWS or Gateway
        self.connect("127.0.0.1", 7497, clientId=1)  # Paper trading port: 7497
        threading.Thread(target=self.run).start()

    def nextValidId(self, orderId: int):
        """Callback when the next valid order ID is received."""
        self.next_valid_order_id = orderId
        print(f"Next valid order ID: {self.next_valid_order_id}")

    def place_order(self, action, quantity, symbol="AAPL", sec_type="STK", exchange="SMART", currency="USD"):
        """Place an order with IBKR."""
        contract = self.create_contract(symbol, sec_type, exchange, currency)
        order = self.create_order(action, quantity)

        if self.next_valid_order_id:
            self.placeOrder(self.next_valid_order_id, contract, order)
            self.order_id += 1
        else:
            print("Waiting for valid order ID...")

    def create_contract(self, symbol, sec_type, exchange, currency):
        """Create a contract for the trade."""
        contract = Contract()
        contract.symbol = symbol
        contract.secType = sec_type
        contract.exchange = exchange
        contract.currency = currency
        return contract

    def create_order(self, action, quantity):
        """Create an order object."""
        order = Order()
        order.action = action  # "BUY" or "SELL"
        order.orderType = "MKT"  # Market order
        order.totalQuantity = quantity
        return order

    def execDetails(self, reqId, contract, execution):
        """Callback when an order is executed."""
        print(f"Order executed: {execution}")
        self.comm_framework.send_execution_confirmation({"status": "executed", "details": execution})

    def error(self, reqId, errorCode, errorString):
        """Callback for errors."""
        print(f"Error: {errorCode} - {errorString}")

    def run(self):
        """Start the execution agent."""
        while True:
            risk_assessment = self.comm_framework.receive_risk_assessment()
            action = "BUY"  # Example: Determine action based on strategy
            quantity = risk_assessment["position_size"]
            self.place_order(action, quantity)
            time.sleep(1)  # Throttle requests