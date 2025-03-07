
---

### **3. `docs/ppo_model_integration.md` (PPO Model Integration)**
```markdown
# AI Trading Bot - PPO Model Integration

## **Overview**
The **Proximal Policy Optimization (PPO)** model is the core of the **strategy agent**. Each ETF has a separate trained PPO model to predict trade actions.

## **PPO Models in Use**
| ETF  | PPO Model File      |
|------|---------------------|
| SPY  | `SPY_ppo.zip`      |
| QQQ  | `QQQ_ppo.zip`      |
| SOXX | `SOXX_ppo.zip`     |
| VGT  | `VGT_ppo.zip`      |
| ARKK | `ARKK_ppo.zip`     |

## **How It Works**
1. The **strategy agent** loads the appropriate PPO model for the ETF.
2. **Data is preprocessed** into a `(1, 50, 3)` format to match the model input.
3. The **model predicts** an action (`BUY`, `SELL`, `HOLD`).
4. The **trade signal** is sent to the **Execution Agent** via **ZeroMQ (5556)**.

## **Code Snippet - Model Loading**
```python
import torch
from stable_baselines3 import PPO

def load_model(ticker):
    model_path = f"models/{ticker}_ppo.zip"
    model = PPO.load(model_path)
    return model
