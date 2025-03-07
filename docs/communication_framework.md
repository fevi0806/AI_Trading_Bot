
---

### **2. `docs/communication_framework.md` (ZeroMQ Communication)**
```markdown
# AI Trading Bot - Communication Framework (ZeroMQ)

## **Overview**
The communication framework for **AI Trading Bot** is built on **ZeroMQ (ZMQ)** to enable efficient and reliable **inter-agent messaging**. Each agent has a designated role and communicates through specific **ports**.

## **Port Assignments**
| Agent                  | Role                  | ZeroMQ Port |
|------------------------|----------------------|------------|
| **CommFramework**      | Central messaging hub | 5555       |
| **Strategy Agent**     | Sends trade signals  | 5556       |
| **Execution Agent**    | Receives trade signals, executes orders | 5557 |
| **Risk Agent**         | Evaluates risks before execution | 5558 |
| **Logging Agent**      | Collects logs & metrics | 5559 |

## **How It Works**
1. **Strategy Agent** publishes trade signals (`BUY`, `SELL`, `HOLD`) to **ZeroMQ Port 5556**.
2. **Execution Agent** subscribes to trade signals from **Port 5556** and executes trades via **IBKR API**.
3. **Risk Agent** listens to incoming orders on **Port 5558** and verifies trade compliance.
4. **Logging Agent** collects logs and sends them to **Loki for Grafana visualization**.

## **Example Message Flow**
1️⃣ **Trade Signal from Strategy Agent**
```json
{
    "ticker": "SPY",
    "signal": "BUY",
    "confidence": 0.87
}
