import time
import logging
import zmq
from ib_insync import IB, Order, Trade

class ExecutionAgent:
    def __init__(self):
        #  Initialize Logging
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s",
            handlers=[logging.StreamHandler(), logging.FileHandler("logs/execution_agent.log")]
        )

        #  Initialize IBKR API Connection
        self.ib = IB()
        self.ib.connect("127.0.0.1", 7497, clientId=2)
        logging.info(" Connected to IBKR API")

        #  Initialize ZeroMQ
        self.context = zmq.Context()
        self.zmq_socket = self.context.socket(zmq.PULL)
        self.zmq_socket.bind("tcp://127.0.0.1:5560")
        logging.info(" ZeroMQ Bound to tcp://127.0.0.1:5556")

        #  Initialize Portfolio & Open Orders
        self.portfolio = {}
        self.open_orders = []

        #  Sync Portfolio and Orders
        self.sync_portfolio()
        self.sync_orders()
        logging.info(" Execution Agent Initialized and Ready!")

    def sync_portfolio(self):
        """Sync portfolio positions from IBKR."""
        logging.info(" Syncing portfolio positions from IBKR...")
        self.portfolio = {}

        positions = self.ib.positions()
        for pos in positions:
            symbol = pos.contract.symbol
            self.portfolio[symbol] = {
                "shares": pos.position,
                "avg_price": pos.avgCost,
            }

        logging.info(f" Portfolio Synced: {self.portfolio}")

    def sync_orders(self):
        """Retrieve and store open orders from IBKR."""
        logging.info(" Fetching open orders from IBKR...")
        self.ib.reqOpenOrders()
        time.sleep(1)  # Ensure IBKR updates before fetching
        self.open_orders = self.ib.orders()

        if self.open_orders:
            logging.info(f" Open Orders Synced: {len(self.open_orders)} orders found")
            for order in self.open_orders:
                logging.info(f" Order: {order}")
        else:
            logging.info(" No open orders detected.")

    def get_account_balance(self):
        """Retrieve available cash balance from IBKR."""
        logging.info(" Fetching account balance...")
        account_summary = self.ib.accountSummary()
        cash_balance = float(account_summary.loc["NetLiquidation", "value"])
        logging.info(f" Account Balance: ${cash_balance}")
        return cash_balance

    def execute_trade(self, ticker, action):
        """Execute a trade based on received signal."""
        logging.info(f" Received Trade Signal: {ticker} - {action}")

        if action == "HOLD":
            logging.info(" No action needed, holding position.")
            return

        # Check if there's an existing open order for the ticker
        existing_order = next((o for o in self.open_orders if o.contract.symbol == ticker), None)
        if existing_order:
            logging.warning(f" Order for {ticker} already exists, skipping duplicate execution.")
            return

        # Get stock contract details
        contract = self.ib.qualifyContracts(self.ib.reqContractDetails(ticker)[0].contract)[0]

        # Determine order action
        order_action = "BUY" if action == "BUY" else "SELL"

        # Calculate trade size
        cash_balance = self.get_account_balance()
        stock_price = self.ib.reqMktData(contract).last
        time.sleep(1)

        if stock_price is None or cash_balance < stock_price * 10:
            logging.warning(f" Not enough balance to trade {ticker}. Skipping order.")
            return

        order_size = int(cash_balance / (stock_price * 10))
        if order_size == 0:
            logging.warning(f" Order size for {ticker} is too small. Skipping.")
            return

        # Create and submit order
        order = Order(
            action=order_action,
            orderType="MKT",
            totalQuantity=order_size
        )

        trade = self.ib.placeOrder(contract, order)
        logging.info(f" Trade Executed: {ticker} - {order_action} {order_size} shares")

        # Store order
        self.open_orders.append(trade)

    def run(self):
        """Main execution loop."""
        logging.info(" Execution Agent Running...")

        while True:
            try:
                if self.zmq_socket.poll(1000):  # Wait for message
                    message = self.zmq_socket.recv_json()
                    ticker, action = message["ticker"], message["signal"]
                    self.execute_trade(ticker, action)

                # Periodically sync open orders
                self.sync_orders()
                time.sleep(5)

            except Exception as e:
                logging.error(f" Execution Error: {e}")

if __name__ == "__main__":
    agent = ExecutionAgent()
    agent.run()
