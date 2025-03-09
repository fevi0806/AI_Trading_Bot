from flask import Flask, request, jsonify
from prometheus_client import Counter, Gauge, generate_latest, CollectorRegistry, CONTENT_TYPE_LATEST

app = Flask(__name__)

# Registro de métricas
registry = CollectorRegistry()
total_trades = Counter('backtest_total_trades', 'Total de operaciones simuladas', registry=registry)
profit_loss_ratio = Gauge('backtest_profit_loss_ratio', 'Relación de Ganancias/Pérdidas', registry=registry)
max_drawdown = Gauge('backtest_max_drawdown', 'Máximo Drawdown (%)', registry=registry)
sharpe_ratio = Gauge('backtest_sharpe_ratio', 'Sharpe Ratio', registry=registry)

@app.route('/metrics')
def metrics():
    """ Expone métricas para Prometheus """
    return generate_latest(registry), 200, {'Content-Type': CONTENT_TYPE_LATEST}

@app.route('/update_metrics', methods=['POST'])
def update_metrics():
    """ Endpoint para actualizar métricas desde el Backtesting """
    data = request.get_json()
    
    total_trades.inc(data.get("total_trades", 0))
    profit_loss_ratio.set(data.get("profit_loss_ratio", 0))
    max_drawdown.set(data.get("max_drawdown", 0))
    sharpe_ratio.set(data.get("sharpe_ratio", 0))
    
    return jsonify({"status": "Metrics updated"}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8001)  # Ahora escucha en el puerto 8001
