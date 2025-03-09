import numpy as np
import pandas as pd

class PerformanceMetrics:
    @staticmethod
    def calculate_sharpe_ratio(returns, risk_free_rate=0.02):
        """ Calcula el Sharpe Ratio """
        excess_returns = returns - risk_free_rate / 252
        return np.mean(excess_returns) / np.std(excess_returns) if np.std(excess_returns) != 0 else 0

    @staticmethod
    def calculate_max_drawdown(returns):
        """ Calcula el máximo drawdown (%) """
        cumulative_returns = (1 + returns).cumprod()
        peak = cumulative_returns.cummax()
        drawdown = (cumulative_returns - peak) / peak
        return drawdown.min() * 100

    @staticmethod
    def calculate_cumulative_return(returns):
        """ Calcula el retorno acumulado en % """
        return (np.prod(1 + returns) - 1) * 100

    @staticmethod
    def evaluate_performance(trade_log, data):
        """ Calcula todas las métricas de rendimiento """
        returns = data['Returns'].dropna()

        return {
            "sharpe_ratio": PerformanceMetrics.calculate_sharpe_ratio(returns),
            "max_drawdown": PerformanceMetrics.calculate_max_drawdown(returns),
            "cumulative_return": PerformanceMetrics.calculate_cumulative_return(returns)
        }
