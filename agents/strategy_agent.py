import os
import pandas as pd
import numpy as np
import yfinance as yf
from stable_baselines3 import PPO
import logging

class StrategyAgent:
    def __init__(self):
        """Initialize StrategyAgent with logging and trade tracking."""
        self.last_trade_day = {}  # ✅ Track last trade date per ticker
        self.market_data_cache = {}  # ✅ Cache fetched market data

        # ✅ Initialize logger properly
        self.logger = logging.getLogger("StrategyAgent")
        self.logger.setLevel(logging.INFO)
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        self.logger.addHandler(console_handler)

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

    def fetch_market_data(self, ticker):
        """Fetch the latest market data for analysis and cache it."""
        if ticker in self.market_data_cache:
            return self.market_data_cache[ticker]  # ✅ Use cached data

        try:
            data = yf.download(ticker, period="60d", interval="1d")
            if data.empty or "Close" not in data.columns:
                self.logger.warning(f"⚠️ No valid market data for {ticker}.")
                return None
            self.market_data_cache[ticker] = data  # ✅ Cache the data
            return data
        except Exception as e:
            self.logger.error(f"❌ Market Data Fetch Error: {e}")
            return None

    def calculate_indicators(self, data):
        """Calculate trend, momentum, and volatility indicators."""
        if data is None or data.empty or "Close" not in data.columns:
            self.logger.error("❌ Indicator Calculation Failed: No Market Data")
            return None

        data["SMA_50"] = data["Close"].rolling(window=50).mean()
        data["SMA_200"] = data["Close"].rolling(window=200).mean()
        data["RSI"] = self.calculate_rsi(data["Close"])
        data["ATR"] = self.calculate_atr(data)
        data["MACD"], data["MACD_signal"] = self.calculate_macd(data)
        return data

    def calculate_rsi(self, close_prices, period=14):
        """Calculate the Relative Strength Index (RSI)."""
        delta = close_prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        
        loss.replace(0, np.nan, inplace=True)  # ✅ Prevent division by zero
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        
        return rsi.fillna(50)  # ✅ Default to neutral RSI (50) if missing

    def calculate_atr(self, data, period=14):
        """Calculate the Average True Range (ATR)."""
        high_low = data["High"] - data["Low"]
        high_close = abs(data["High"] - data["Close"].shift())
        low_close = abs(data["Low"] - data["Close"].shift())
        tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
        return tr.rolling(period).mean()

    def calculate_macd(self, data, fast=12, slow=26, signal=9):
        """Calculate MACD and its signal line."""
        if len(data) < slow:
            self.logger.warning(f"⚠️ Not enough data to calculate MACD.")
            return np.zeros(len(data)), np.zeros(len(data))  
        
        fast_ema = data["Close"].ewm(span=fast, adjust=False).mean()
        slow_ema = data["Close"].ewm(span=slow, adjust=False).mean()
        macd = fast_ema - slow_ema
        signal_line = macd.ewm(span=signal, adjust=False).mean()
        return macd, signal_line

    def market_regime(self, data):
        """Detect if the market is bullish, bearish, or sideways."""
        if data["SMA_50"].iloc[-1] > data["SMA_200"].iloc[-1]:  
            return "BULLISH"
        elif data["SMA_50"].iloc[-1] < data["SMA_200"].iloc[-1]:  
            return "BEARISH"
        return "SIDEWAYS"

    def predict_trade_signal(self, ticker):
        """Generate a trade signal using the defined strategy."""
        model = self.load_ppo_model(ticker)
        data = self.fetch_market_data(ticker)

        if model is None or data is None:
            return "HOLD"

        data = self.calculate_indicators(data)
        if data is None:
            return "HOLD"

        market_condition = self.market_regime(data)
        latest_rsi = data["RSI"].iloc[-1]
        latest_macd = data["MACD"].iloc[-1]
        latest_macd_signal = data["MACD_signal"].iloc[-1]

        self.logger.info(f"📊 Market Regime for {ticker}: {market_condition}")
        self.logger.info(f"🔹 RSI: {latest_rsi:.2f}, MACD: {latest_macd:.2f}, MACD Signal: {latest_macd_signal:.2f}")

        last_trade_date = self.last_trade_day.get(ticker)
        if last_trade_date:
            days_since_last_trade = (data.index[-1] - last_trade_date).days
            if days_since_last_trade < 10:
                self.logger.info(f"⏳ Trade cooldown active ({days_since_last_trade}/10 days). Holding position.")
                return "HOLD"

        if market_condition in ["BULLISH", "SIDEWAYS"] and latest_rsi < 30:
            self.last_trade_day[ticker] = data.index[-1]
            self.logger.info(f"✅ Trade Signal: BUY for {ticker}")
            return "BUY"

        elif market_condition in ["BULLISH", "SIDEWAYS"] and latest_rsi > 65:
            self.last_trade_day[ticker] = data.index[-1]
            self.logger.info(f"✅ Trade Signal: SELL for {ticker}")
            return "SELL"

        self.logger.info(f"⏳ Trade Signal: HOLD for {ticker}")
        return "HOLD"
