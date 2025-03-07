# 🏗️ AI_Trading_Bot - System Architecture

## **🔹 Overview**
The AI_Trading_Bot is structured using **multiple agents** communicating via **ZMQ** for real-time execution and analysis.

## **📡 Communication Setup**
| **Agent**               | **ZMQ Role**  | **Port** |
|-------------------------|--------------|---------|
| `MarketDataAgent`       | PUB          | `5555`  |
| `SentimentAgent`        | SUB          | `5557`  |
| `StrategyAgent`         | PUB          | `5558`  |
| `ExecutionAgent`        | SUB / PUB    | `5558 / 5559`  |
| `RiskManagementAgent`   | SUB          | `5559`  |
| `LoggingMonitoringAgent` | SUB          | `5560`  |

## **⚙️ AI Model Integration**
- ✅ **Uses PPO reinforcement learning models** (`models/{ticker}_ppo.zip`).
- ✅ AI model **receives market data & evaluates trading signals**.
- ✅ **Feedback loop integrated** to adjust trading decisions based on rewards.

📌 **Next Steps:**  
- Ensure **Risk Agent is correctly receiving trade feedback**.  
- Implement **training loop for reinforcement learning updates**.  
