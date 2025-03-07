# 📊 AI_Trading_Bot - Logging & Monitoring

## **🔹 Logging System**
We use **Loki** for collecting logs and **Grafana** for visualization.

## **📡 Log Sources**
| **Agent**                 | **Log Type** |
|---------------------------|-------------|
| `CommFramework`           | System logs, messaging events |
| `StrategyAgent`           | Trade signals, AI decisions |
| `ExecutionAgent`          | Executed trades, confirmations |
| `RiskManagementAgent`     | Risk evaluations, trade modifications |

## **📊 Grafana Dashboard Setup**
- ✅ **Real-time trade monitoring**
- ✅ **Performance tracking of AI models**
- ✅ **Risk analysis visualization**

📌 **Next Steps:**  
- Ensure **all logs are properly collected** in backtesting mode.  
- Implement **Grafana alerts for trade anomalies**.  
