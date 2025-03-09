import zmq
import json
import time
import logging
import os
import numpy as np
import requests  # <-- Importamos requests para enviar métricas a Prometheus
from stable_baselines3 import PPO
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from utils.logger import setup_logger
from agents.comm_framework import CommFramework

PROMETHEUS_PUSHGATEWAY = "http://localhost:9091/metrics/job/trade_signals"

class StrategyAgent:
    def __init__(self, comm_framework):
        self.comm = comm_framework
        self.trade_signal_pub = self.comm.create_publisher("StrategyAgent")
        self.market_data_sub = self.comm.create_subscriber("StrategyAgent")
        self.logger = setup_logger("StrategyAgent", "logs/strategy_agent.log")
        self.running = True  # ✅ Allows graceful shutdown

    def load_ppo_model(self, ticker):
        """Load PPO model for a specific ticker."""
        model_path = f"models/{ticker}_ppo.zip"
        if not os.path.exists(model_path):
            self.logger.error(f"❌ Model not found: {model_path}")
            return None
        try:
            model = PPO.load(model_path)
            self.logger.info(f"📥 Loaded Model: {model_path}")
            return model
        except Exception as e:
            self.logger.error(f"❌ Model Load Error: {e}")
            return None

    def send_trade_signal_to_prometheus(self, ticker, signal):
        """Enviar trade signals a Prometheus."""
        try:
            data = f'trade_signals{{ticker="{ticker}", signal="{signal}"}} 1\n'
            response = requests.post(PROMETHEUS_PUSHGATEWAY, data=data)
            if response.status_code == 200:
                self.logger.info(f"📊 Sent trade signal to Prometheus: {ticker} -> {signal}")
            else:
                self.logger.warning(f"⚠️ Failed to send trade signal to Prometheus: {response.text}")
        except Exception as e:
            self.logger.error(f"❌ Prometheus Push Error: {e}")

    def predict_trade_signal(self, ticker):
        """Generate a trade signal using the PPO model or fallback random choice."""
        model = self.load_ppo_model(ticker)
        if model is None:
            return None

        try:
            # Placeholder logic: Replace with actual prediction logic
            signal = np.random.choice(["BUY", "SELL", "HOLD"])
            self.logger.info(f"📊 {ticker} Signal: {signal}")
            return signal
        except Exception as e:
            self.logger.error(f"❌ Model Prediction Error for {ticker}: {e}")
            return None

    def run(self):
        """Continuously processes market data and generates trade signals."""
        self.logger.info("🚀 Strategy Agent Started.")

        while self.running:
            try:
                if self.market_data_sub:
                    message = self.market_data_sub.recv_string(flags=zmq.NOBLOCK)  # ✅ Non-blocking receive
                    market_data = json.loads(message)

                    # ✅ Ensure market data contains necessary information
                    if not isinstance(market_data, list) or not market_data:
                        self.logger.warning("⚠️ Received malformed or empty market data.")
                        continue
                    
                    ticker = market_data[0].get("Ticker")
                    if not ticker:
                        self.logger.warning("⚠️ Market data missing 'Ticker' field.")
                        continue

                    signal = self.predict_trade_signal(ticker)
                    if signal:
                        trade_signal = json.dumps({"ticker": ticker, "signal": signal})

                        # ✅ Send trade signal to Prometheus
                        self.send_trade_signal_to_prometheus(ticker, signal)

                        # ✅ Ensure publisher is available before sending
                        if self.trade_signal_pub and not self.trade_signal_pub.closed:
                            self.trade_signal_pub.send_string(trade_signal)
                            self.logger.info(f"📧 Trade Signal Sent: {trade_signal}")
                        else:
                            self.logger.warning("⚠️ Cannot send trade signal: Publisher socket closed.")

            except zmq.Again:
                pass  # ✅ No message available, continue looping
            except Exception as e:
                self.logger.error(f"❌ Error in StrategyAgent: {e}")

            time.sleep(60)  # ✅ Controlled delay to avoid infinite loop issues

    def stop(self):
        """Gracefully stops the StrategyAgent."""
        self.logger.info("🛑 Stopping Strategy Agent...")
        self.running = False  # ✅ Signal loop to exit
