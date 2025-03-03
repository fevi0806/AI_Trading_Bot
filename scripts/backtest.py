import pandas as pd
from models.predictive_model import PredictiveModel
from utils.logger import setup_logger

# Initialize logger
logger = setup_logger()

def backtest():
    """
    Run a backtest using historical data.
    """
    try:
        # Load historical data
        data = pd.read_csv("data/datasets/historical_data.csv")
        logger.info("Historical data loaded successfully.")

        # Preprocess data
        X = data.drop(columns=["target"])  # Features
        y = data["target"]  # Target variable (e.g., price change)

        # Split data into training and testing sets
        split = int(0.8 * len(data))
        X_train, X_test = X[:split], X[split:]
        y_train, y_test = y[:split], y[split:]

        # Initialize and train the predictive model
        model = PredictiveModel()
        logger.info("Training predictive model...")
        model.train(X_train, y_train)

        # Make predictions
        logger.info("Running backtest...")
        predictions = model.predict(X_test)

        # Evaluate performance
        backtest_results = pd.DataFrame({
            "Actual": y_test,
            "Predicted": predictions.flatten()
        })
        backtest_results.to_csv("data/backtest_results.csv", index=False)
        logger.info("Backtest completed. Results saved to data/backtest_results.csv.")

    except Exception as e:
        logger.error(f"Error during backtest: {e}")

if __name__ == "__main__":
    backtest()