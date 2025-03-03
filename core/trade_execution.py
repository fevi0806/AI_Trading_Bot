from ib_insync import *
import logging
import time

class TradeExecution:
    def __init__(self, paper_trading=True):
        self.ib = IB()
        self.port = 7497 if paper_trading else 7496
        self.logger = logging.getLogger("TradeExecution")

        try:
            self.ib.connect('127.0.0.1', self.port, clientId=1)
            self.logger.info("Connected to IBKR API.")
        except Exception as e:
            self.logger.error(f"Failed to connect to IBKR: {e}")
            exit(1)

    def execute_trade(self, ticker, action, quantity):
        if not self.ib.isConnected():
            self.logger.error("IBKR connection lost.")
            return

        contract = Stock(ticker, 'SMART', 'USD')
        order = MarketOrder(action, quantity)

        trade = self.ib.placeOrder(contract, order)
        self.ib.sleep(2)
        self.logger.info(f"Trade executed: {action} {quantity} shares of {ticker}")

        return trade

    def disconnect(self):
        self.ib.disconnect()
        self.logger.info("Disconnected from IBKR.")
