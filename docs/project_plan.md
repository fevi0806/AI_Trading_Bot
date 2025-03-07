AI Trading Bot - Project Documentation

1. Project Overview

Project Name: AI_Trading_Bot

Goal:

To develop a fully autonomous AI-driven trading bot that executes trades based on predictive models and reinforcement learning. The bot will integrate market data, AI strategies, risk management, and trade execution using IBKR and ZeroMQ for agent communication.

Key Features:

Live Trading & Paper Trading with IBKR

Historical Data Backtesting for Strategy Optimization

AI-Powered Strategy using PPO (Reinforcement Learning)

Risk Management & Portfolio Allocation

Logging & Monitoring (Loki & Grafana)

ZeroMQ-Based Communication Between Agents

2. Roadmap & Phases

Phase 1: System Setup & Core Infrastructure (✅ Completed)

✅ IBKR API integration for trade execution

✅ Market data collection via yfinance

✅ Logging system setup with Loki & Grafana

✅ Initial ZeroMQ agent communication established

Phase 2: Live Trading & Strategy Implementation (✅ Completed)

✅ Implemented Moving Average & Sentiment-based strategy

✅ PPO Reinforcement Learning Model for trade decision-making

✅ Successful paper trading execution

✅ Order tracking & risk management logic implemented

Phase 3: Historical Data Backtesting (⏳ In Progress)

⚠ Ensure correct ZeroMQ communication between agents

⚠ Strategy Agent loads historical data correctly for PPO models

⚠ Execution Agent properly simulates trade execution

⚠ Backtesting framework aligns with live trading logic

⚠ Trade logs from backtesting are stored and analyzed

Phase 4: Advanced AI & Optimization (🚧 Not Started Yet)

🔜 Reinforcement learning fine-tuning (custom reward functions)

🔜 Expanding dataset for improved model training

🔜 Enhancing portfolio allocation strategies

3. File & Folder Structure

AI_Trading_Bot/
├── agents/
│   ├── comm_framework.py      # Handles ZeroMQ communication
│   ├── data_agent.py          # Collects market data
│   ├── execution_agent.py     # Executes trades (Backtesting mode)
│   ├── execution_agent1.py    # Executes trades (Live Trading mode)
│   ├── risk_agent.py          # Manages risk logic
│   ├── strategy_agent.py      # Generates trade signals (Backtesting mode)
│   ├── strategy_agent1.py     # Generates trade signals (Live Trading mode)
│   ├── logging_monitoring_agent.py
│   └── integration_test.py
├── config/
│   ├── api_keys.yaml          # Stores IBKR & other API keys
│   ├── model_config.yaml      # Configuration for PPO models
├── core/
│   ├── trading_engine.py      # Manages trade execution logic
│   ├── portfolio_manager.py   # Handles portfolio allocation
├── data/
│   ├── data_preprocessor.py   # Prepares data for AI models
│   ├── datasets/              # Contains historical market data
├── models/
│   ├── QQQ_ppo.zip            # PPO model for QQQ
│   ├── SPY_ppo.zip            # PPO model for SPY
│   ├── SOXX_ppo.zip           # PPO model for SOXX
│   ├── VGT_ppo.zip            # PPO model for VGT
│   ├── ARKK_ppo.zip           # PPO model for ARKK
├── logs/                      # Stores execution logs
├── utils/
│   ├── data_utils.py          # Functions for fetching & processing market data
│   ├── zmq_utils.py           # Helper functions for ZeroMQ
├── main.py                    # Entry point for running the bot
├── requirements.txt            # Python dependencies
└── README.md                   # Project documentation

4. ZeroMQ Communication & Port Assignments

Agent

Socket Type

Port

Function

Comm Framework

PUB

5557

Broadcasts market data to all agents

Comm Framework

REP

5558

Handles agent requests

Strategy Agent

PUB

5559

Sends trade signals

Execution Agent

SUB

5559

Receives trade signals from Strategy Agent

Execution Agent

PUB

5560

Sends trade execution feedback

Risk Agent

SUB

5560

Receives execution feedback for risk tracking

5. PPO Model Management

Each ticker has its own PPO model:

QQQ_ppo.zip, SPY_ppo.zip, SOXX_ppo.zip, VGT_ppo.zip, ARKK_ppo.zip

Models are loaded dynamically per ticker in Strategy Agent.

Ensure correct data preprocessing before feeding into the model.

6. Identified Issues & Fixes

Current Issues:

ZeroMQ Port Conflicts

Execution Agent must listen on 5559 for trade signals.

Comm Framework must handle agent request responses on 5558.

PPO Model Loading Issue

Strategy Agent should load ticker_ppo.zip dynamically instead of a generic PPO model.

Data Handling Issue in Strategy Agent

Missing columns in historical data.

Proper OHLCV column selection required.

Backtesting Execution Failure

Execution Agent not placing trades based on signals.

Verify trade signal handling logic.

Immediate Fixes:

✔ Fix ZeroMQ Configuration – Ensure each agent connects to the correct port.✔ Correct PPO Model Loading – Each ticker uses its designated PPO model.✔ Fix Data Handling in Strategy Agent – Proper selection of OHLCV columns.✔ Verify Execution Agent Logic – Ensure trades are executed based on strategy signals.✔ Test Backtesting Flow – Run a simulation to validate full pipeline.

7. Next Steps

Verify & Implement Fixes: Ensure all pending issues are resolved.

Run Full Backtesting Simulation: Validate historical trade execution.

Improve Reinforcement Learning Training: Optimize model performance.

Enhance Portfolio Allocation & Risk Management: Implement dynamic position sizing.

Transition to Live Trading with Optimized Strategy: Once backtesting is validated.

8. Change Management Process

All code changes must be approved before implementation.

Every modification must be documented in this file.

No deviations from roadmap or structure without justification.

Final Notes:

This document will serve as the single source of truth for project development, tracking progress, and managing all implementations moving forward.

🚀 This document should be kept up-to-date with every change.

